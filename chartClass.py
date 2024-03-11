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


class Chart:
    def __init__(self, SOC, chart_id, parent=None) -> None:
        self.__chart_id = chart_id
        self.__soc = SOC
        self.__chart_type = self.__determineChartType()
        self.__tf_item_type = self.__setChartType()
        self.__tf_item_name = setTfName(self.__chart_id)
        self.__parent = parent
        if self.__tf_item_type != None:
            self.__initialWrite()
            self.__importTerraform()

    def __determineChartType(self):
        url = f"https://api.{self.__soc._getRealm()}.signalfx.com/v2/chart/{self.__chart_id}"
        headers = {"X-SF-TOKEN": self.__soc._getAPIKey()}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        chart_type = response.json()['options']['type']
        return chart_type

    def __importTerraform(self):
        if not self.__soc._getFuse():
            terraformInit(self.__soc._getCWD(),
                          self.__soc._getAPIKey(), self.__soc._getRealm(), self.__soc._getVerbose())
        terraformImport(f"{self.__tf_item_type}.{self.__tf_item_name}", self.__chart_id, self.__soc._getCWD(
        ), self.__soc._getAPIKey(), self.__soc._getRealm(), self.__soc._getVerbose())
        self.__terraform = terraformState(f"{self.__tf_item_type}.{self.__tf_item_name}", self.__chart_id, self.__soc._getCWD(
        ), self.__soc._getAPIKey(), self.__soc._getRealm(), self.__soc._getVerbose())
        if isinstance(self.__terraform, int):
            return
        self.__terraform = '\n'.join(line for line in self.__terraform.split(
            '\n') if not re.search(r'\b(url|id|config_id|tags)\s*=', line))
        return

    def __initialWrite(self):
        if self.__parent == None:
            with open(f"{self.__soc._getCWD()}/{self.__tf_item_name}.tf", "w") as f:
                f.write(
                    f"resource \"{self.__tf_item_type}\" \"{self.__tf_item_name}\" {{\n")
                f.write(f"}}\n")
        else:
            with open(f"{self.__soc._getCWD()}/{self.__parent._getDashboardName()[0]}.tf", "a") as f:
                f.write(
                    f"resource \"{self.__tf_item_type}\" \"{self.__tf_item_name}\" {{\n")
                f.write(f"}}\n")

    def __setChartType(self):
        try:
            type = chart_naming[self.__chart_type]
        except KeyError:
            type = 1
        if type != 1:
            return type
        else:
            return None

    def _getTfItemType(self):
        return self.__tf_item_type

    def _getTerraform(self) -> str:
        return self.__terraform

    def _produceFile(self):
        with open(f"{self.__soc._getCWD()}/{self.__tf_item_name}.tf", "w") as f:
            f.write(self.__terraform)
        return
