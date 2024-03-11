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

import uuid
import os
import re
import json
import subprocess
import shutil
import requests
from collections import defaultdict

# Silence RE

import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)

# Terraform Components


def terraformInit(working_dir, o11y_api_token, o11y_realm, verbose=False):
    command = ["terraform", "init", "-var",
               f"o11y_api_token={o11y_api_token}", "-var", f"o11y_realm={o11y_realm}"]

    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=working_dir)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        if verbose:
            print(f"Error executing Terraform init: {stderr.decode()}")
        return 1
    else:
        if verbose:
            print(f"Terraform init successful: {stdout.decode()}")
        return 0


def terraformImport(resource_address, resource_id, working_dir, o11y_api_token, o11y_realm, verbose=False):
    command = ["terraform", "import", "-var",
               f"o11y_api_token={o11y_api_token}", "-var", f"o11y_realm={o11y_realm}", resource_address, resource_id]

    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=working_dir)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        if verbose:
            print(f"Error executing Terraform import: {stderr.decode()}")
    else:
        if verbose:
            print(f"Terraform import successful: {stdout.decode()}")


def terraformState(resource_address, resource_id, working_dir, o11y_api_token, o11y_realm, verbose=False):
    command = ["terraform", "state", "show", resource_address]

    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=working_dir)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        if verbose:
            print(f"Error executing Terraform state: {stderr.decode()}")
        return ""
    else:
        return stdout.decode()


def terraformValidate(working_dir, o11y_api_token, o11y_realm, verbose=False):
    command = ["terraform", "validate", "-var",
               f"o11y_api_token={o11y_api_token}", "-var", f"o11y_realm={o11y_realm}"]

    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=working_dir)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        if verbose:
            print(f"Error executing Terraform validate: {stderr.decode()}")
        return 1
    else:
        if verbose:
            print(f"Terraform validate successful: {stdout.decode()}")
        return 0

# Content Matrix


chart_naming = {
    'List': 'signalfx_list_chart',
    'SingleValue': 'signalfx_single_value_chart',
    'Text': 'signalfx_text_chart',
    'TimeSeriesChart': 'signalfx_time_chart',
    'Event': 'signalfx_event_feed_chart',
    'TableChart': 'signalfx_table_chart',
    'Heatmap': 'signalfx_heatmap_chart',
}


def getChartType(chart_type):
    return chart_naming.get(chart_type, 1)

# Terraform Management


def handleDuplicateCharts(cwd, verbose=False):
    files = [f for f in os.listdir(cwd) if os.path.isfile(
        os.path.join(cwd, f)) and f.endswith('.tf')]

    resource_files = defaultdict(list)
    for file in files:
        with open(os.path.join(cwd, file), 'r') as f:
            content = f.read()
            chart_resources = re.findall(
                r'resource "(\w+_chart)" "([\w-]+)" {', content)
            for resource_type, resource_name in chart_resources:
                resource_files[resource_name].append(file)

    duplicates_only = {resource_name: filenames for resource_name,
                       filenames in resource_files.items() if len(filenames) > 1}

    if not duplicates_only:
        if verbose:
            print("No Duplicates Found!")
        return
    else:
        if verbose:
            print("The following chart ids are duplicated across multiple files:")
            for chart_id, filenames in duplicates_only.items():
                print(f"{chart_id} in {filenames}")

    for chart_id, filenames in duplicates_only.items():
        for i, file in enumerate(filenames[1:], start=1):
            with open(os.path.join(cwd, file), 'r') as f:
                content = f.read()
            new_chart_id = f"{chart_id}-{str(uuid.uuid4())[:8]}"
            content = content.replace(chart_id, new_chart_id)
            with open(os.path.join(cwd, file), 'w') as f:
                f.write(content)


def cleanup(cwd):
    shutil.rmtree(os.path.join(cwd, ".terraform"), ignore_errors=True)
    os.remove(os.path.join(cwd, ".terraform.lock.hcl"))
    os.remove(os.path.join(cwd, "terraform.tfstate"))
    try:
        os.remove(os.path.join(cwd, "terraform.tfstate.backup"))
    except FileNotFoundError:
        pass  # If only run for a chart, this will error


def updateIds(cwd):
    # for .tf files in cwd
    for filename in [f for f in os.listdir(cwd) if os.path.isfile(os.path.join(cwd, f)) and f.endswith('.tf')]:
        print("brrrrrrr")
        with open(os.path.join(cwd, filename), 'r') as file:
            content = file.read()

        # Find all chart resources and their names
        chart_resources = re.findall(
            r'resource "(signalfx_[\w_]+_chart)" "([\w_-]+)"', content)
        chart_ids = {resource_name for resource_type,
                     resource_name in chart_resources}

        # Replace hard-coded chart IDs in dashboard section with references to chart resources
        for resource_type, resource_name in chart_resources:
            content = re.sub(
                rf'chart_id = "{resource_name}"',
                f'chart_id = {resource_type}.{resource_name}.id',
                content
            )

        # Write the updated content back to the file
        with open(os.path.join(cwd, filename), 'w') as file:
            file.write(content)


def orphanCheck(cwd):
    all_chart_resources = set()
    all_dashboard_resources = []

    for filename in [f for f in os.listdir(cwd) if os.path.isfile(os.path.join(cwd, f)) and f.endswith('.tf')]:
        print('for 1')
        with open(os.path.join(cwd, filename), 'r') as file:
            content = file.read()

        # Find all chart resources and their IDs
        chart_resources = re.findall(
            r'resource "signalfx_[\w_]+_chart" "([\w_-]+)"', content)
        all_chart_resources.update(chart_resources)

        # Find all dashboard resources and their associated chart IDs
        dashboard_resources = re.findall(
            r'resource "signalfx_dashboard" "([\w_-]+)" {.*?chart_id = "([^"]*)".*?}', content, re.DOTALL)
        all_dashboard_resources.extend(dashboard_resources)

    # Check for orphan charts across all files
    print(all_dashboard_resources)
    for filename in [f for f in os.listdir(cwd) if os.path.isfile(os.path.join(cwd, f)) and f.endswith('.tf')]:
        print("for 2")
        with open(os.path.join(cwd, filename), 'r') as file:
            content = file.read()

        # Check if each chart ID in the dashboard resources is referenced as a resource ID
        for dashboard_name, chart_id in all_dashboard_resources:
            print("beep boop next level")
            if chart_id not in all_chart_resources:
                # This is an orphan chart ID, remove it
                content = re.sub(
                    'chart\s*{\s*chart_id\s*=\s*"([^"]*)".*?}', '', content, flags=re.DOTALL)
        # Check if each chart resource is referenced in a dashboard
        for chart_id in all_chart_resources:
            if not any(chart_id == id for _, id in all_dashboard_resources):
                # This is an orphan chart resource, remove it
                content = re.sub(
                    rf'# signalfx_[\w_]+_chart.{chart_id}:\nresource "signalfx_[\w_]+_chart" "{chart_id}" {{.*?}}\n# signalfx_[\w_]+_chart.{chart_id}:\n', '', content, flags=re.DOTALL)
                # Write the updated content back to the file
        with open(os.path.join(cwd, filename), 'w') as file:
            file.write(content)


def setTfName(name):
    # Replace spaces, periods and '@' with underscores
    name = re.sub(r'[ @.]', '_', name)

    # Ensure the name starts with a letter or underscore
    if not re.match(r'^[a-zA-Z_]', name):
        name = '_' + name

    # Replace any character that is not a letter, digit, underscore, or dash with an underscore
    name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)

    return name
