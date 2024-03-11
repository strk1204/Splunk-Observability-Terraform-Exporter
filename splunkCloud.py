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

class SplunkObservabilityCloud:
    def __init__(self, token, realm, cwd, verbose=False):
        self.__token = token
        self.__realm = realm
        self.__cwd = cwd
        self.__fuse = False
        self.__verbose = verbose

    def _getRealm(self) -> str:
        return self.__realm

    def _getAPIKey(self) -> str:
        return self.__token

    def _getCWD(self) -> str:
        return self.__cwd

    def _getFuse(self) -> bool:
        # Fuse boolean - Used to determine if the local Terraform state has been initialized
        if self.__fuse:
            return True
        else:
            self.__fuse = True
            return False

    def _getVerbose(self) -> bool:
        return self.__verbose
