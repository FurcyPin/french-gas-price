This is a demo project to demonstrate [spark-frame](https://pypi.org/project/spark-frame/)'s capabilities.

It uses an Open Data dataset about French gas stations.
It gives the list of all gas stations in France and for each of them, information such as:
- the address
- the type of gas available
- the current price for each type of gas
- the opening times for each day of the week

It is updated every 10 minutes and is maintained by the French Government.

I chose this dataset because its schema is relatively complex, 
with multiple levels of nesting, which is quite uncommon,
as most open datasets have a simple and flat structure. 
The dataset exists in two versions: v1 and v2, which also make it excellent 
for demonstrating the utility of spark-frame's data-diff features.

## The data

- The v1 of the dataset is available 
  [here](https://www.prix-carburants.gouv.fr/rubrique/opendata/).
  It is a zipped folder containing a xml file.
- The v2 of the dataset is available 
  [here](https://data.economie.gouv.fr/explore/dataset/prix-des-carburants-en-france-flux-instantane-v2/export/)


## How to use

### Setup

#### Create a virtual environment
```
poetry env use python3
```

#### Download dependencies
```
poetry update
```

#### Download the data
```
poetry run python download_data.py
```

This will download today's version of three datasets 
which correspond to the same data in different formats. 
- `data/v1_xml`
- `data/v2_csv`
- `data/v2_json`
- `data/v2_parquet`

The datasets are partitioned by day.

