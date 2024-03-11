# Splunk Observability Terraform Exporter
Version 1.0.1 (SignalFX 9.1.1)

This project provides a tool for exporting Splunk Observability Cloud configurations to Terraform. It interacts with the Splunk Observability Cloud API to fetch configurations for dashboard groups, dashboards, and charts, and generates corresponding Terraform configuration files. This allows you to manage your Splunk Observability Cloud setup using infrastructure as code practices with Terraform.

## Table of Contents

- [Splunk Observability Terraform Exporter](#splunk-observability-terraform-exporter)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Scope](#scope)
  - [Tests](#tests)
  - [License](#license)
  - [Trademarks](#trademarks)
  - [Contact](#contact)


## Installation

1. Clone this repository to your local machine.
2. Ensure that Terraform is installed on your machine. If not, you can download it from the [official Terraform website](https://www.terraform.io/downloads.html).
3. Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```
Alternatively, a Docker package with all prerequisites is available. This allows you to run the exporter in a containerized environment without needing to manually install Terraform and the Python packages. You can run the Docker package using the following command:

```bash
docker run -i -v $HOME/somedir:/opt/app/terraform_output strk1204/stt:latest
```

This command maps the `$HOME/somedir` directory on your host system to the `/opt/app/terraform_output` directory in the Docker container. Any files that the Docker container writes to `/opt/app/terraform_output` will appear in `$HOME/somedir` on your host system, and vice versa.

Please replace `somedir` with the actual directory where you want the output files to be saved. If the directory does not exist, Docker will create it for you.

This application requires the usage of Python3.10 or newer.

## Usage

This script exports resources from Splunk Observability Cloud to Terraform. It supports dashboards, dashboard groups, and charts. The script accepts the following command-line arguments:

- `--realm` or `-r`: Specifies the realm. Defaults to "au0".
- `--api-key` or `-a`: Specifies the API key. This is required.
- `--dashboard` or `-db`: Specifies the ID of a dashboard to export.
- `--group` or `-dg`: Specifies the ID of a dashboard group to export.
- `--chart` or `-ch`: Specifies the ID of a chart to export.
- `--verbose` or `-v`: Enables verbose output.

At least one of `--dashboard`, `--group`, or `--chart` must be provided.

The script performs the following operations:

1. Creates a directory named "terraform_output" in the current working directory.
2. Creates a `SplunkObservabilityCloud` object.
3. Depending on the provided arguments, creates a `Dashboard`, `DashboardGroup`, or `Chart` object.
4. Calls the `_produceFile()` method on the created object to export the resource to Terraform.
5. Calls `handleDuplicateCharts()` and `cleanup()` functions to remove duplicate charts and clean up temporary files.

## Scope

The current scope and feature set of the Splunk Observability Terraform Exporter are focused on three main components of the Splunk Observability Cloud:

- **Dashboards**: The tool can export configurations of dashboards from the Splunk Observability Cloud. This includes all the settings and configurations of a dashboard, such as its layout, the charts it contains, and its metadata.

The use of this function, will require that the "dashboard_group" value be populated, after running. It is currently a requirement that this is present in the Terraform code. A placeholder will be left in it's place. 

- **Dashboard Groups**: The tool supports exporting of dashboard groups. A dashboard group in Splunk Observability Cloud is a collection of dashboards. The exporter can retrieve the configuration of these groups, including the list of dashboards they contain.

- **Charts**: The tool can export individual charts from the Splunk Observability Cloud. A chart is a visual representation of your data in Splunk Observability Cloud. The exporter can retrieve all the settings and configurations of a chart, such as its type (e.g., line chart, bar chart), the metrics it displays, and its formatting options.

**NOTE**: All exports are limited by the SingalFX Splunk Observability Cloud Terraform provider. Any limitations that exist in that provider, will exist in this exporter. 

## Tests

Testing sutie incomplete

## License

This project is licensed under the terms of the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## Trademarks

Splunk, Splunk Observability Cloud, and SignalFX are trademarks or registered trademarks of Splunk Inc. in the United States and other countries. All other brand names, product names, or trademarks belong to their respective owners.

## Contact

For any questions or concerns, you can reach out through GitHub or send an email to [develop@seankunkler.com](mailto:develop@seankunkler.com).

---

Sean Kunkler - 2024