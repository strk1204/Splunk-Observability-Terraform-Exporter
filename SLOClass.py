# Copyright 2024 Sean Kunkler

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
from helperFunctions import *


class SLO:
    def __init__(self, slo_id, SOC):
        self.__slo_id = slo_id
        self.__soc = SOC
        self.__slo_name = self.__fetchName()
        self.__tf_item_name = setTfName(self.__slo_name)
        self.__initialWrite()
        self.__importTerraform()

    def __importTerraform(self):
        if not self.__soc._getFuse():
            terraformInit(self.__soc._getCWD(),
                          self.__soc._getAPIKey(), self.__soc._getRealm(), self.__soc._getVerbose())
        terraformImport(f"signalfx_slo.{self.__tf_item_name}", self.__slo_id, self.__soc._getCWD(
        ), self.__soc._getAPIKey(), self.__soc._getRealm(), self.__soc._getVerbose())
        self.__terraform = terraformState(f"signalfx_slo.{self.__tf_item_name}", self.__slo_id, self.__soc._getCWD(
        ), self.__soc._getAPIKey(), self.__soc._getRealm(), self.__soc._getVerbose())
        if isinstance(self.__terraform, int):
            return
        self.__terraform = '\n'.join(line for line in self.__terraform.split(
            '\n') if not re.search(r'\b(url|id|config_id|tags)\s*=', line))
        return

    def __initialWrite(self):
        with open(f"{self.__soc._getCWD()}/{self.__tf_item_name}.tf", "w") as f:
            f.write(
                f"resource \"signalfx_slo\" \"{self.__tf_item_name}\" {{\n")
            f.write(f"}}\n")

    def __fetchName(self):
        url = f"https://api.{self.__soc._getRealm()}.signalfx.com/v2/slo/{self.__slo_id}"
        headers = {"X-SF-TOKEN": self.__soc._getAPIKey()}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        slo_name = response.json()['name']
        return slo_name

    def _produceTerraform(self):
        with open(f"{self.__soc._getCWD()}/{self.__tf_item_name}.tf", "w") as f:
            f.write(self.__terraform)
        return
