import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests

MAVEN_URL = "https://repo1.maven.org/maven2"


@dataclass
class JavaDependency:
    group_id: str
    artifact_id: str
    version: str
    classifier: Optional[str] = None

    @property
    def __classifier_str(self):
        if self.classifier is None:
            return ""
        else:
            return f"-{self.classifier}"

    @property
    def jar_name(self) -> str:
        return f"{self.artifact_id}-{self.version}{self.__classifier_str}.jar"

    @property
    def jar_path(self) -> Path:
        return Path(f"jars/{self.jar_name}")

    def download(self):
        if self.jar_path.exists():
            print(f"Getting {self.jar_path}: already downloaded")
            return
        group_id = self.group_id.replace(".", "/")
        artifact_id = self.artifact_id
        version = self.version
        jar_name = self.jar_name
        url = f"""{MAVEN_URL}/{group_id}/{artifact_id}/{version}/{jar_name}"""
        print(url)
        os.makedirs("jars", exist_ok=True)
        response = requests.get(url)
        with self.jar_path.open("wb") as output_file:
            output_file.write(response.content)
        print(f"Getting {self.jar_path}: downloaded from Maven Central")
