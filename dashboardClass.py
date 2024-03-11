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

import hcl
import requests

from chartClass import *


class Dashboard:
    def __init__(self, dashboard_id, SOC, dashboard_group=None):
        self.__dashboard_id = dashboard_id
        self.__soc = SOC
        self.__dashboard_name = self.__fetchName()
        self.__tf_item_name = setTfName(self.__dashboard_name)
        self.__charts = []
        self.__dashboard_group = dashboard_group
        if self.__dashboard_group != None:
            self.__initialWrite()
            self.__importTerraform()
            self.__sortCharts()

    def __initialWrite(self):
        with open(f"{self.__soc._getCWD()}/{self.__dashboard_name}.tf", "w") as f:
            f.write(
                f"resource \"signalfx_dashboard\" \"{self.__tf_item_name}\" {{\n")
            f.write(f"}}\n")

    def __importTerraform(self):
        if not self.__soc._getFuse():
            terraformInit(self.__soc._getCWD(),
                          self.__soc._getAPIKey(), self.__soc._getRealm(), self.__soc._getVerbose())
        terraformImport(f"signalfx_dashboard.{self.__tf_item_name}", self.__dashboard_id, self.__soc._getCWD(
        ), self.__soc._getAPIKey(), self.__soc._getRealm(), self.__soc._getVerbose())
        self.__terraform = terraformState(f"signalfx_dashboard.{self.__tf_item_name}", self.__dashboard_id, self.__soc._getCWD(
        ), self.__soc._getAPIKey(), self.__soc._getRealm(), self.__soc._getVerbose())
        if isinstance(self.__terraform, int):
            return
        if self.__dashboard_group:
            self.__terraform = re.sub(r'\b(dashboard_group)\s*=\s*".*"',
                                      r'\1 = {}'.format(self.__dashboard_group), self.__terraform)
        if self.__dashboard_group != "PLACEHOLDER":
            self.__terraform = re.sub(
                r'\b(parent)\s*=\s*".*"', r'\1 = {}'.format(self.__dashboard_group), self.__terraform)
        self.__terraform = '\n'.join(line for line in self.__terraform.split(
            '\n') if not re.search(r'\b(url|id|config_id)\s*=', line))

        return

    def __fetchName(self) -> str:
        url = f"https://api.{self.__soc._getRealm()}.signalfx.com/v2/dashboard/{self.__dashboard_id}"
        headers = {"X-SF-TOKEN": self.__soc._getAPIKey()}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()["name"]

    def _getTerraform(self) -> str:
        return self.__terraform

    def __sortCharts(self):
        parsed_config = hcl.loads(self.__terraform)
        if 'chart' not in parsed_config['resource']['signalfx_dashboard'][self.__tf_item_name]:
            return
        # Extract the charts
        charts = parsed_config['resource']['signalfx_dashboard'][self.__tf_item_name]['chart']

        # if chart is not an array, make it an array of one object
        if not isinstance(charts, list):
            charts = [charts]

        for chart in charts:
            # Create a new Chart object and append it to self.__charts
            new_chart = Chart(self.__soc, chart["chart_id"], self)
            if new_chart._getTfItemType() != None:
                self.__charts.append(new_chart)

    def _getDashboardName(self) -> str:
        return [self.__dashboard_name, self.__tf_item_name]

    def _getName(self) -> str:
        return self.__dashboard_name

    def _setName(self, name) -> None:
        self.__dashboard_name = name
        self.__tf_item_name = setTfName(self.__dashboard_name)
        self.__initialWrite()
        self.__importTerraform()
        self.__sortCharts()
        return

    def _setGroup(self, group) -> None:
        self.__dashboard_group = group
        self.__initialWrite()
        self.__importTerraform()
        self.__sortCharts()
        return

    def _produceFile(self):
        with open(f"{self.__soc._getCWD()}/{self.__dashboard_name}.tf", "w") as f:
            f.write(self.__terraform)
            for chart in self.__charts:
                if chart._getTerraform() != 1:
                    terraform_string = str(chart._getTerraform())
                    f.write(terraform_string)
                    f.write("\n")
                    f.write(terraform_string.split('\n')[0])
                    f.write("\n")
        return
