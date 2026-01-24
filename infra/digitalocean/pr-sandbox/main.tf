# DigitalOcean PR Sandbox Infrastructure
# Creates ephemeral droplets/apps per PR for isolated testing
#
# Usage:
#   terraform init
#   terraform apply -var="pr_number=123" -var="branch_name=feat/my-feature"
#
# Auto-destroy: TTL-based cleanup via GitHub Actions on PR close

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.34"
    }
  }

  # Remote state in DO Spaces (optional - configure bucket)
  # backend "s3" {
  #   endpoint                    = "nyc3.digitaloceanspaces.com"
  #   region                      = "us-east-1"  # Required but ignored
  #   bucket                      = "ipai-terraform-state"
  #   key                         = "pr-sandbox/terraform.tfstate"
  #   skip_credentials_validation = true
  #   skip_metadata_api_check     = true
  #   skip_region_validation      = true
  # }
}

provider "digitalocean" {
  # Token from DIGITALOCEAN_TOKEN env var
}

# Variables
variable "pr_number" {
  description = "Pull request number"
  type        = string
}

variable "branch_name" {
  description = "Branch name (sanitized for resource naming)"
  type        = string
}

variable "repo_name" {
  description = "Repository name"
  type        = string
  default     = "odoo-ce"
}

variable "ttl_hours" {
  description = "Time-to-live in hours before auto-destroy"
  type        = number
  default     = 24
}

variable "droplet_size" {
  description = "Droplet size slug"
  type        = string
  default     = "s-2vcpu-4gb"
}

variable "region" {
  description = "DigitalOcean region"
  type        = string
  default     = "nyc3"
}

# Locals
locals {
  # Sanitize branch name for resource naming
  safe_branch = replace(lower(var.branch_name), "/[^a-z0-9-]/", "-")
  resource_prefix = "pr-${var.pr_number}-${substr(local.safe_branch, 0, 20)}"

  common_tags = [
    "pr-sandbox",
    "pr:${var.pr_number}",
    "repo:${var.repo_name}",
    "ttl:${var.ttl_hours}h",
    "created:${timestamp()}"
  ]
}

# SSH Key (use existing or create)
data "digitalocean_ssh_keys" "all" {}

# VPC for isolation
resource "digitalocean_vpc" "sandbox" {
  name     = "${local.resource_prefix}-vpc"
  region   = var.region
  ip_range = "10.${100 + (var.pr_number % 155)}.0.0/16"

  lifecycle {
    create_before_destroy = true
  }
}

# Firewall
resource "digitalocean_firewall" "sandbox" {
  name = "${local.resource_prefix}-fw"

  droplet_ids = [digitalocean_droplet.sandbox.id]

  # Inbound: SSH + HTTP/HTTPS + Odoo ports
  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "8069-8071"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # Outbound: Allow all
  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "icmp"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}

# Cloud-init script for droplet setup
locals {
  cloud_init = <<-EOF
    #cloud-config
    package_update: true
    package_upgrade: false

    packages:
      - docker.io
      - docker-compose
      - git
      - curl
      - jq

    write_files:
      - path: /opt/sandbox/info.json
        content: |
          {
            "pr_number": "${var.pr_number}",
            "branch": "${var.branch_name}",
            "repo": "${var.repo_name}",
            "created_at": "${timestamp()}",
            "ttl_hours": ${var.ttl_hours}
          }

      - path: /opt/sandbox/setup.sh
        permissions: '0755'
        content: |
          #!/bin/bash
          set -euo pipefail
          cd /opt/sandbox

          # Clone repo at PR branch
          git clone --depth 1 --branch "${var.branch_name}" \
            "https://github.com/jgtolentino/${var.repo_name}.git" repo || \
          git clone --depth 1 "https://github.com/jgtolentino/${var.repo_name}.git" repo

          cd repo

          # Start services (if docker-compose exists)
          if [[ -f docker-compose.yml ]]; then
            docker compose up -d postgres || true
            sleep 10
            docker compose up -d odoo-core || true
          fi

          # Mark as ready
          echo "ready" > /opt/sandbox/status

    runcmd:
      - systemctl enable docker
      - systemctl start docker
      - usermod -aG docker root
      - mkdir -p /opt/sandbox
      - /opt/sandbox/setup.sh &> /opt/sandbox/setup.log &
  EOF
}

# Droplet
resource "digitalocean_droplet" "sandbox" {
  name     = "${local.resource_prefix}-droplet"
  region   = var.region
  size     = var.droplet_size
  image    = "ubuntu-22-04-x64"
  vpc_uuid = digitalocean_vpc.sandbox.id

  ssh_keys = [for key in data.digitalocean_ssh_keys.all.ssh_keys : key.fingerprint]

  user_data = local.cloud_init

  tags = local.common_tags

  lifecycle {
    create_before_destroy = true
  }
}

# DNS record (optional - requires domain configured)
# resource "digitalocean_record" "sandbox" {
#   domain = "insightpulseai.net"
#   type   = "A"
#   name   = "pr-${var.pr_number}"
#   value  = digitalocean_droplet.sandbox.ipv4_address
#   ttl    = 300
# }

# Outputs
output "droplet_id" {
  value       = digitalocean_droplet.sandbox.id
  description = "Droplet ID for cleanup"
}

output "droplet_ip" {
  value       = digitalocean_droplet.sandbox.ipv4_address
  description = "Public IP address"
}

output "droplet_name" {
  value       = digitalocean_droplet.sandbox.name
  description = "Droplet name"
}

output "sandbox_url" {
  value       = "http://${digitalocean_droplet.sandbox.ipv4_address}:8069"
  description = "Odoo URL (once services start)"
}

output "ssh_command" {
  value       = "ssh root@${digitalocean_droplet.sandbox.ipv4_address}"
  description = "SSH connection command"
}

output "ttl_expiry" {
  value       = timeadd(timestamp(), "${var.ttl_hours}h")
  description = "Expected TTL expiry time"
}
