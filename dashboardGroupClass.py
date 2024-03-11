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

from dashboardClass import *


class DashboardGroup:
    def __init__(self, group_id, SOC):
        self.__group_id = group_id
        self.__soc = SOC
        self.__dashboards = []
        self.__group_name = self.__fetchName()
        self.__tf_item_name = setTfName(self.__group_name)
        self.__initialWrite()
        self.__importTerraform()
        self.__fetchChildDashboards()
        self.__checkDuplicateChildren()

    def __fetchName(self) -> str:
        url = f"https://api.{self.__soc._getRealm()}.signalfx.com/v2/dashboardgroup/{self.__group_id}"
        headers = {"X-SF-TOKEN": self.__soc._getAPIKey()}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()["name"]

    def __fetchChildDashboards(self):
        group_id = f"signalfx_dashboard_group.{self.__tf_item_name}.id"
        url = f"https://api.{self.__soc._getRealm()}.signalfx.com/v2/dashboardgroup/{self.__group_id}"
        headers = {"X-SF-TOKEN": self.__soc._getAPIKey()}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        for dashboard in data.get('dashboards'):
            new_dashboard = Dashboard(dashboard, self.__soc, group_id)
            self.__dashboards.append(new_dashboard)
        return

    def __initialWrite(self):
        with open(f"{self.__soc._getCWD()}/{self.__group_name}-Group.tf", "w") as f:
            f.write(
                f"resource \"signalfx_dashboard_group\" \"{self.__tf_item_name}\" {{\n")
            f.write(f"}}\n")

    def __importTerraform(self):
        if not self.__soc._getFuse():
            terraformInit(self.__soc._getCWD(),
                          self.__soc._getAPIKey(), self.__soc._getRealm(), self.__soc._getVerbose())
        terraformImport(f"signalfx_dashboard_group.{self.__tf_item_name}", self.__group_id, self.__soc._getCWD(
        ), self.__soc._getAPIKey(), self.__soc._getRealm(), self.__soc._getVerbose())
        self.__terraform = terraformState(f"signalfx_dashboard_group.{self.__tf_item_name}", self.__group_id, self.__soc._getCWD(
        ), self.__soc._getAPIKey(), self.__soc._getRealm(), self.__soc._getVerbose())
        self.__terraform = '\n'.join(line for line in self.__terraform.split(
            '\n') if not re.search(r'\b(url|id|config_id)\s*=', line))
        return

    def __checkDuplicateChildren(self):
        name_count = {}
        for dashboard in self.__dashboards:
            name = dashboard._getName()
            if name in name_count:
                name_count[name] += 1
                new_name = f"{name}{name_count[name]}"
                dashboard._setName(new_name)
            else:
                name_count[name] = 0

    def _produceFile(self):
        with open(f"{self.__soc._getCWD()}/{self.__group_name}-Group.tf", "w") as f:
            f.write(self.__terraform)
        for dashboard in self.__dashboards:
            dashboard._produceFile()
        return
