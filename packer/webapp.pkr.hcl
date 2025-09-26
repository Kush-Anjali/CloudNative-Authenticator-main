packer {
  required_plugins {
    googlecompute = {
      version = ">= 1.1.4"
      source  = "github.com/hashicorp/googlecompute"
    }
  }
}

variable "gcp_project_id" {
  type      = string
  default   = ""
  sensitive = true
}

variable "source_image_family" {
  type    = string
  default = "centos-stream-8"
}

variable "ssh_username" {
  type    = string
  default = "csye6225"
}

variable "ssh_user_group" {
  type    = string
  default = "csye6225"
}

variable "zone" {
  type    = string
  default = "us-central1-b"
}

variable "image_family" {
  type    = string
  default = "my-webapp"
}

variable "disk_type" {
  type    = string
  default = "pd-balanced"
}

variable "disk_size" {
  type    = string
  default = "20"
}

variable "app_artifact_path" {
  type    = string
  default = "../app_artifact/webapp.zip"
}

variable "requirement_path" {
  type    = string
  default = "scripts/requirements.txt"
}

variable "mysql_root_password" {
  type      = string
  sensitive = true
}

variable "mysql_database_name" {
  type    = string
  default = "webApp"
}

variable "mysql_user" {
  type    = string
  default = "dev-1"
}

variable "mysql_user_password" {
  type      = string
  sensitive = true
}

source "googlecompute" "webapp" {
  project_id          = var.gcp_project_id
  source_image_family = var.source_image_family
  ssh_username        = var.ssh_username
  zone                = var.zone
  image_name          = "${var.image_family}-${formatdate("YYYY-MM-DD-hh-mm-ss", timestamp())}"
  image_family        = var.image_family
  disk_type           = var.disk_type
  disk_size           = var.disk_size
}

build {
  sources = ["source.googlecompute.webapp"]

  provisioner "shell" {
    script = "scripts/create_user.sh"
  }

  provisioner "file" {
    source      = var.requirement_path
    destination = "/tmp/requirements.txt"
  }

  provisioner "shell" {
    script = "scripts/install_dependencies.sh"
  }

  provisioner "file" {
    source      = var.app_artifact_path
    destination = "/home/${var.ssh_username}/webapp.zip"
  }

  provisioner "shell" {
    inline = [
      "cd /home/${var.ssh_username}",
      "unzip webapp.zip",
      "chown -R ${var.ssh_username}:${var.ssh_username} *"
    ]
  }

  provisioner "file" {
    source      = "./webapp.service"
    destination = "/tmp/webapp.service"
  }

  provisioner "file" {
    source      = "scripts/config.yaml"
    destination = "/tmp/config.yaml"
  }

  provisioner "shell" {
    script = "scripts/setup_ops_agent.sh"
  }

  provisioner "shell" {
    script = "scripts/app_start_up.sh"
    environment_vars = [
      "PROJECT_LOC=/home/${var.ssh_username}/cloud/webapp",
      "LOG_DIR=/var/log/myapp"
    ]
  }
}
