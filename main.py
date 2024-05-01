import datetime
import os
import sys

from pyspark.sql import SparkSession, Column
from pyspark.sql import functions as f
from spark_frame import nested
from spark_frame.data_diff import DiffFormatOptions, compare_dataframes
from spark_frame.schema_utils import schema_from_json
from spark_frame.transformations import transform_all_field_names
from spark_frame.transformations import parse_json_columns

from java_dependency import JavaDependency
from v1_schema import v1_schema

day = datetime.date.today().isoformat()

os.environ["PYSPARK_PYTHON"] = sys.executable

spark_xml = JavaDependency(
    group_id="com.databricks",
    artifact_id="spark-xml_2.12",
    version="0.17.0",
)
spark_xml.download()

spark = (SparkSession.builder
         .appName("french-gas-prices")
         .config("spark.driver.extraClassPath", str(spark_xml.jar_path))
         .config("spark.sql.parquet.int96RebaseModeInWrite", "CORRECTED")
         .config("spark.sql.session.timeZone", "UTC")
         .getOrCreate())

xml_options = {
    "rootTag": "pdv_list",
    "rowTag": "pdv",
    "charset": "ISO-8859-1",
    "mode": "FAILFAST"
}

df_v1_xml_raw = spark.read.format("xml").schema(schema_from_json(v1_schema)).options(**xml_options).load(
    f"data/v1_xml/day={day}/PrixCarburants_instantane_ruptures.xml")


def clean_field_names(name: str):
    name = name.lower()
    if name.startswith("_"):
        return name[1:]
    else:
        return name

df_v1_xml_2 = df_v1_xml_raw.transform(transform_all_field_names, clean_field_names)

carburants = ["E10", "E85", "SP95", "SP98", "Gazole", "GPLc"]
carburants_array = f.array([f.lit(c) for c in carburants])


def get_from(col_name, name):
    """Iterate over the array column `col_name` and only keep the records matching this name"""
    return f.filter(f.col(col_name), lambda c: c["nom"] == f.lit(name))


def clean_rupture_type(gas_type):
    res = f.array_max(get_from("rupture", gas_type)["type"])
    res = f.when(res != f.lit(""), res)
    return res


df_v1_xml_3 = df_v1_xml_2.withColumnsRenamed({
    "cp": "code postal",
}).withColumns({
    "services proposes": "services.service",
    "carburants disponibles": f.col("prix.nom"),
    "carburants indisponibles":
        f.nullif(
            f.filter(carburants_array, lambda c: ~f.array_contains(f.col("prix.nom"), c)),
            f.array()
        ),
    "e10_maj": get_from("prix", "E10")[0]["maj"],
    "e85_maj": get_from("prix", "E85")[0]["maj"],
    "sp95_maj": get_from("prix", "SP95")[0]["maj"],
    "sp98_maj": get_from("prix", "SP98")[0]["maj"],
    "gazole_maj": get_from("prix", "Gazole")[0]["maj"],
    "gplc_maj": get_from("prix", "GPLc")[0]["maj"],

    "e10_prix": get_from("prix", "E10")[0]["valeur"],
    "e85_prix": get_from("prix", "E85")[0]["valeur"],
    "sp95_prix": get_from("prix", "SP95")[0]["valeur"],
    "sp98_prix": get_from("prix", "SP98")[0]["valeur"],
    "gazole_prix": get_from("prix", "Gazole")[0]["valeur"],
    "gplc_prix": get_from("prix", "GPLc")[0]["valeur"],

    "e10_rupture_debut": f.array_max(get_from("rupture", "E10")["debut"]),
    "e85_rupture_debut": f.array_max(get_from("rupture", "E85")["debut"]),
    "sp95_rupture_debut": f.array_max(get_from("rupture", "SP95")["debut"]),
    "sp98_rupture_debut": f.array_max(get_from("rupture", "SP98")["debut"]),
    "gazole_rupture_debut": f.array_max(get_from("rupture", "Gazole")["debut"]),
    "gplc_rupture_debut": f.array_max(get_from("rupture", "GPLc")["debut"]),

    "e10_rupture_type": clean_rupture_type("E10"),
    "e85_rupture_type": clean_rupture_type("E85"),
    "sp95_rupture_type": clean_rupture_type("SP95"),
    "sp98_rupture_type": clean_rupture_type("SP98"),
    "gazole_rupture_type": clean_rupture_type("Gazole"),
    "gplc_rupture_type": clean_rupture_type("GPLc"),

    "horaires": f.col("horaires").dropFields("`automate-24-24`"),

    "code_departement": f.substring(f.col("code postal"), 0, 2),

    "automate 24-24 (oui/non)":
        f.when(f.col("horaires.automate-24-24") == f.lit(1), f.lit("Oui")).otherwise(f.lit("Non"))
})

df_v1_xml_4 = df_v1_xml_3.transform(nested.with_fields, {
    "horaires.jour!": lambda jour: jour.dropFields("value"),
    "prix!": lambda prix: prix.dropFields("value"),
    "rupture!": lambda rupture: rupture.dropFields("value"),
}).transform(nested.with_fields, {
    "horaires.jour!.horaire!": lambda horaire: horaire.dropFields("value"),
}).drop(
    "services"
)

# # # # # # JSON # # # # # #

df_v2_json_raw = spark.read.format("json").load(f"data/v2_json/day={day}/data.json")

df_v2_json_v2 = df_v2_json_raw.withColumnsRenamed({
    "cp": "code postal",
    "carburants_disponibles": "carburants disponibles",
    "carburants_indisponibles": "carburants indisponibles",
    "horaires_automate_24_24": "automate 24-24 (oui/non)",
    "services_service": "services proposes"
})

df_v2_json_v3 = df_v2_json_v2.withColumns({
    "e10_maj": f.col("e10_maj").cast("timestamp"),
    "e85_maj": f.col("e85_maj").cast("timestamp"),
    "sp95_maj": f.col("sp95_maj").cast("timestamp"),
    "sp98_maj": f.col("sp98_maj").cast("timestamp"),
    "gazole_maj": f.col("gazole_maj").cast("timestamp"),
    "gplc_maj": f.col("gplc_maj").cast("timestamp"),
    "e10_prix": f.col("e10_prix").cast("double"),
    "e85_prix": f.col("e85_prix").cast("double"),
    "sp95_prix": f.col("sp95_prix").cast("double"),
    "sp98_prix": f.col("sp98_prix").cast("double"),
    "gazole_prix": f.col("gazole_prix").cast("double"),
    "gplc_prix": f.col("gplc_prix").cast("double"),
    "latitude": f.col("latitude").cast("double"),
    "longitude": f.col("longitude").cast("double"),
})


def to_utc_timestamp(ts: Column) -> Column:
    return f.to_timestamp(ts)


df_v2_json_v4 = df_v2_json_v3.withColumns({
    "e10_maj": to_utc_timestamp(f.col("e10_maj")),
    "e10_rupture_debut": to_utc_timestamp(f.col("e10_rupture_debut")),
    "e85_maj": to_utc_timestamp(f.col("e85_maj")),
    "e85_rupture_debut": to_utc_timestamp(f.col("e85_rupture_debut")),
    "gazole_maj": to_utc_timestamp(f.col("gazole_maj")),
    "gazole_rupture_debut": to_utc_timestamp(f.col("gazole_rupture_debut")),
    "gplc_maj": to_utc_timestamp(f.col("gplc_maj")),
    "gplc_rupture_debut": to_utc_timestamp(f.col("gplc_rupture_debut")),
    "sp95_maj": to_utc_timestamp(f.col("sp95_maj")),
    "sp95_rupture_debut": to_utc_timestamp(f.col("sp95_rupture_debut")),
    "sp98_maj": to_utc_timestamp(f.col("sp98_maj")),
    "sp98_rupture_debut": to_utc_timestamp(f.col("sp98_rupture_debut")),
})


df_v2_json_v5 = df_v2_json_v4.transform(parse_json_columns, "horaires")

df_v2_json_v6 = df_v2_json_v5.transform(nested.with_fields, {
    "horaires.jour!.horaire": lambda jour:
    f.coalesce(
        f.from_json(jour["horaire"], "ARRAY<STRUCT<`@fermeture`: STRING, `@ouverture`: STRING>>"),
        f.array(
            f.from_json(jour["horaire"], "STRUCT<`@fermeture`: STRING, `@ouverture`: STRING>"),
        ),
    )
})

df_v2_json_v7 = df_v2_json_v6.withColumns({
    "prix":
        f.coalesce(
            f.from_json("prix", "ARRAY<STRUCT<`@id`: STRING, `@maj`: TIMESTAMP, `@nom`: STRING, `@valeur`: STRING>>"),
            f.array(
                f.from_json("prix", "STRUCT<`@id`: STRING, `@maj`: TIMESTAMP, `@nom`: STRING, `@valeur`: STRING>")
            ),
        ),
    "rupture":
        f.from_json("rupture", "ARRAY<STRUCT<`@debut`:STRING,`@fin`:STRING,`@id`:STRING,`@nom`:STRING,`@type`:STRING>>"),
})


def clean_field_names(name: str):
    name = name.lower()
    if name.startswith("@") :
        return name[1:]
    else:
        return name

df_v2_json_v8 = df_v2_json_v7.transform(
    transform_all_field_names, clean_field_names
).transform(nested.with_fields, {
    "horaires": lambda df: df["horaires"].dropFields("`automate-24-24`"),
}).drop("services", "horaires_jour")


df_v2_json_v9 = df_v2_json_v8.transform(nested.with_fields, {
    "prix!.id": lambda prix: prix["id"].cast("BIGINT"),
    "prix!.valeur": lambda prix: prix["valeur"].cast("DOUBLE"),
    "rupture!.debut": lambda rupture: rupture["debut"].cast("TIMESTAMP"),
    "rupture!.id": lambda rupture: rupture["id"].cast("BIGINT"),
    "horaires.jour!.id": lambda jour: jour["id"].cast("BIGINT"),
    "horaires.jour!.horaire!.ouverture": lambda horaire: horaire["ouverture"].cast("DOUBLE"),
    "horaires.jour!.horaire!.fermeture": lambda horaire: horaire["fermeture"].cast("DOUBLE"),
}).transform(nested.with_fields, {
    "horaires.jour!.horaire": lambda jour:
        f.when(
            (f.array_size(jour["horaire"]) == f.lit(1))
            & jour["horaire"][0]["fermeture"].isNull()
            & jour["horaire"][0]["ouverture"].isNull(), f.lit(None)
        ).otherwise(
            jour["horaire"]
        )
})

# nested.print_schema(df_json)
# nested.print_schema(df_csv)
# nested.print_schema(df_json)
# nested.print_schema(df_xml)

join_cols = ["id", "prix!.id", "horaires.jour!.id"]

from spark_frame.data_diff.schema_diff import diff_dataframe_schemas
df_v1 = df_v1_xml_4.select(sorted(df_v1_xml_4.columns))
df_v2 = df_v2_json_v9.select(sorted(df_v2_json_v9.columns))

print(diff_dataframe_schemas(df_v1, df_v2, join_cols).diff_str)

# df_xml.write.parquet("french_gas_price_v1")
# df_json.write.parquet("french_gas_price_v2")

diff_result = compare_dataframes(df_v1, df_v2, join_cols=join_cols)
# diff_result.diff_df_shards[""].printSchema()
diff_format_options = DiffFormatOptions(
    nb_top_values_kept_per_column=200,
    left_df_alias="v1",
    right_df_alias="v2",
)

diff_result.export_to_html(
    title="Comparaison des sources v1 vs v2",
    diff_format_options=diff_format_options
)

