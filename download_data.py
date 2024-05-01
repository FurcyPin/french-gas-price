import datetime
import os
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import requests


@dataclass
class SourceFile:
    table: str
    url: str
    format: str
    version: int


v2_csv = SourceFile(
    table="v2_csv",
    url="https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/exports/csv?lang=fr&timezone=Europe%2FParis&use_labels=true&delimiter=%3B",
    format="csv",
    version=2
)

v2_json = SourceFile(
    table="v2_json",
    url="https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/exports/json?lang=fr&timezone=Europe%2FParis",
    format="json",
    version=2
)

v2_parquet = SourceFile(
    table="v2_parquet",
    url="https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/exports/parquet?lang=fr&timezone=Europe%2FParis",
    format="parquet",
    version=2
)

v1_xml = SourceFile(
    table="v1_xml",
    url="https://donnees.roulez-eco.fr/opendata/instantane_ruptures",
    format="xml",
    version=1
)

sources = [v1_xml, v2_csv, v2_json, v2_parquet]


def _download_file(name: str, url: str, format: str):
    response = requests.get(url)
    data = response.content

    today = datetime.date.today().isoformat()
    today_path = Path(f"data/{name}/day={today}")
    os.makedirs(today_path, exist_ok=True)

    with (today_path / f"data.{format}").open("wb") as output_file:
        output_file.write(data)


def _download_v1(name: str, url: str):
    response = requests.get(url)
    compressed_data = BytesIO(response.content)

    today = datetime.date.today().isoformat()
    today_path = Path(f"data/{name}/day={today}")
    os.makedirs(today_path, exist_ok=True)

    with (ZipFile(compressed_data, "r") as zip_file,
          (today_path / f"PrixCarburants_instantane_ruptures.xml").open("w", encoding="ISO-8859-1") as output_file):
        file_content = zip_file.read("PrixCarburants_instantane_ruptures.xml").decode(encoding="ISO-8859-1")
        output_file.write(file_content)


def download_source(source: SourceFile):
    if source.version == 1:
        _download_v1(source.table, source.url)
    else:
        _download_file(source.table, source.url, source.format)


def download_all():
    for source in sources:
        download_source(source)


download_all()
