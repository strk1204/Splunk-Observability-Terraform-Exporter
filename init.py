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

import argparse
import os
import sys

from dashboardGroupClass import *
from SLOClass import *
from detectorClass import *
from splunkCloud import *

parser = argparse.ArgumentParser(
    description='Exporting Splunk Observability Cloud resources to Terraform.')
parser.add_argument('--realm', '-r', type=str, help='realm', default="au0")
# Requirement handled later due to docker support
parser.add_argument('--api-key', '-a', type=str,
                    help='api key', required=False)
parser.add_argument('--dashboard', '-db', type=str, help='Dashboard ID')
parser.add_argument('--group', '-dg', type=str, help='Dashboard Group ID')
parser.add_argument('--chart', '-ch', type=str, help='Chart ID')
parser.add_argument('--slo', '-sl', type=str, help='SLO ID')
parser.add_argument('--detector', '-dt', type=str, help='Detector ID')
parser.add_argument('--verbose', '-v', action='store_true',
                    help='Enable verbose output')
args = parser.parse_args()

# Get user input
if args.api_key == None:
    args.api_key = input("Enter your API key: ")
if args.dashboard == None and args.group == None and args.chart == None and args.slo == None and args.detector == None:
    print("No resource specified, please specify a resource to create")
    user_choice = input(
        "Would you like to create a dashboard, dashboard group, chart, SLO, or detector? (db/dg/ch/sl/dt): ")
    match user_choice:
        case "db":
            args.dashboard = input("Enter the dashboard id: ")
        case "dg":
            args.group = input("Enter the dashboard group id: ")
        case "ch":
            args.chart = input("Enter the chart id: ")
        case "sl":
            args.slo = input("Enter the SLO id: ")
        case "dt":
            args.detector = input("Enter the detector id: ")
        case _:
            print("Invalid choice, please try again")
            sys.exit(1)

if args.verbose == None:
    args.verbose = False

# Get the current working directory
cwd = os.getcwd()
# Append "terraform_output" to the current working directory
output_dir = os.path.join(cwd, "terraform_output")
# If the directory doesn't exist, create it
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Download main.tf from the specified URL if it doesn't exist.if not os.path.exists(os.path.join(output_dir, "main.tf")):
if not os.path.exists(os.path.join(output_dir, "main.tf")):
    url = "https://raw.githubusercontent.com/strk1204/Splunk-Observability-Terraform-Exporter/main/adt-resources/main.tf"
    r = requests.get(url)
    with open(os.path.join(output_dir, "main.tf"), "wb") as f:
        f.write(r.content)

# If there are any Terraform files other than main.tf, ask the user for permission to delete them.
if len([f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f)) and f.endswith('.tf') and f != "main.tf"]) > 0:
    user_choice = input(
        "There are terraform files present in the output directory that aren't main.tf, would you like to remove them? (y/n): ")
    match user_choice:
        case "y":
            for f in os.listdir(output_dir):
                if os.path.isfile(os.path.join(output_dir, f)) and f.endswith('.tf') and f != "main.tf":
                    os.remove(os.path.join(output_dir, f))
            try:   
                cleanup(output_dir)
            except FileNotFoundError:
                pass # Possibly some but not all tf files existed
        case "n":
            print("Exiting...")
            sys.exit(0)
        case _:
            print("Invalid choice, exiting...")
            sys.exit(1)

# Create a SplunkObservabilityCloud object
SplunkCloud = SplunkObservabilityCloud(
    args.api_key, args.realm, output_dir, args.verbose)
if args.dashboard:
    dashboard = Dashboard(args.dashboard, SplunkCloud)
    dashboard._setGroup("PLACEHOLDER")
    dashboard._produceFile()
    updateIds(output_dir)
    orphanCheck(output_dir)
elif args.group:
    group = DashboardGroup(args.group, SplunkCloud)
    group._produceFile()
    updateIds(output_dir)
    orphanCheck(output_dir)
elif args.chart:
    chart = Chart(SplunkCloud, args.chart, None)
    chart._produceFile()
elif args.slo:
    slo = SLO(args.slo, SplunkCloud)
    slo._produceTerraform()
elif args.detector:
    detector = Detector(SplunkCloud, args.detector)
    detector._produceTerraform()

# Cleanup Functions
handleDuplicateCharts(output_dir, args.verbose)
cleanup(output_dir)
print("Terraform files have been created in the terraform_output directory!")
