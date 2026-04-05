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
  location      = "us-central1"
  storage_class = "STANDARD"
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

resource "google_bigquery_dataset" "stackoverflow_stg" {
  dataset_id = "stackoverflow_stg"
  location   = "us-central1"
}
resource "google_bigquery_dataset" "analytics" {
  dataset_id = "analytics"
  location   = "us-central1"
}
