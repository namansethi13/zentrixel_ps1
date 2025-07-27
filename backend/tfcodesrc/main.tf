provider "google" {
  project = var.project_id
  region  = "us-central1"
}

resource "google_project" "project" {
  name       = "hackathon-zentrixel"
  project_id = var.project_id
  billing_account = var.billing_account

  lifecycle {
  prevent_destroy = false
  }
}

resource "google_project_service" "pubsub" {
  project = google_project.project.project_id
  service = "pubsub.googleapis.com"
  disable_on_destroy = false
}

resource "google_pubsub_topic" "topic" {
  name    = "tweet_topic"
  project = google_project.project.project_id
}

resource "google_pubsub_subscription" "subscription" {
  name  = "tweet_topic-sub"
  topic = google_pubsub_topic.topic.name
  project = google_project.project.project_id
}

resource "google_service_account" "sa" {
  account_id   = "citypulsehackathon-sa"
  display_name = "CityPulse Hackathon Service Account"
  description  = "Service account for CityPulse Hackathon"
  project      = google_project.project.project_id
}

resource "google_project_iam_member" "sa_pubsub_admin" {
  project = google_project.project.project_id
  role    = "roles/pubsub.admin"
  member  = "serviceAccount:${google_service_account.sa.email}"
}

resource "google_service_account_key" "sa_key" {
  service_account_id = google_service_account.sa.name
  keepers = {
    service_account_email = google_service_account.sa.email
  }
}

#firestore configuration
resource "google_project_service" "firestore" {
  project = google_project.project.project_id
  service = "firestore.googleapis.com"
  disable_on_destroy = false
}

#resource "google_firestore_database" "default" {
#  name        = "(default)"
#  project     = google_project.project.project_id
#  location_id = "asia-south1" 
#  type        = "FIRESTORE_NATIVE"
#}

resource "google_project_iam_member" "sa_firestore_user" {
  project = google_project.project.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.sa.email}"
}