output "service_account_email" {
  value = google_service_account.sa.email
}

output "service_account_key_private" {
  value     = google_service_account_key.sa_key.private_key
  sensitive = true
}

output "project_id" {
  value = google_project.project.project_id
}
