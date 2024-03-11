FROM python:alpine3.19

# Initial files
COPY requirements.txt /dist/requirements.txt
COPY *.py /opt/app/

# Dependencies
RUN apk add --no-cache \
    curl \
    wget

# Python config
RUN python3 -m ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools && \
    pip install --no-cache-dir --no-dependencies -r /dist/requirements.txt

# Terraform install
RUN release=$(curl -s https://api.github.com/repos/hashicorp/terraform/releases/latest |  grep tag_name | cut -d: -f2 | tr -d \"\,\v | awk '{$1=$1};1') && \
    wget https://releases.hashicorp.com/terraform/${release}/terraform_${release}_linux_amd64.zip && \
    unzip terraform_${release}_linux_amd64.zip && \
    mv terraform /usr/bin/terraform && \
    rm -R terraform_${release}_linux_amd64.zip

# Clean up
RUN rm -R /dist

# Run
WORKDIR /opt/app
RUN mkdir /opt/app/terraform_output && \
    wget https://raw.githubusercontent.com/strk1204/Splunk-Observability-Terraform-Exporter/main/adt-resources/main.tf -O /opt/app/terraform_output/main.tf
CMD ["python", "init.py"]
