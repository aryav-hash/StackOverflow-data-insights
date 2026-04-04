terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "7.20.0"
    }
  }
}

provider "google" {
  # Configurations
  credentials = "./keys/airport-creds.json"
  project     = "airport-dashboard-492216"
  region      = "us-central1"
}

resource "google_storage_bucket" "auto-expire" {
  name          = "airport-dashboard-492216-bucket"
  location      = "US"
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

# this is to store the
terraform {
  backend "gcs" {
    bucket = "airport-dashboard-492216-bucket"
    prefix = "terraform/state"
  }
}