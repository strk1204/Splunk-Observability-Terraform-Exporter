terraform {
    required_providers {
        signalfx = {
            source  = "splunk-terraform/signalfx"
            version = "9.1.1"
        }
    }
}

provider "signalfx" {
    auth_token = var.o11y_api_token
    api_url    = "https://api.${var.o11y_realm}.signalfx.com"
}

variable "o11y_realm" {
    type     = string
    default  = "au0"
    nullable = false
}

variable "o11y_api_token" {
    type     = string
    nullable = false
}
