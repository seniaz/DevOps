output "worker_ip" {
  description = "IP address of the worker VM"
  value       = libvirt_domain.worker.network_interface[0].addresses[0]
}

output "db_ip" {
  description = "IP address of the DB VM"
  value       = libvirt_domain.db.network_interface[0].addresses[0]
}

output "ansible_inventory" {
  description = "Generated Ansible inventory content"
  value = <<-EOT
  [workers]
  worker ansible_host=${libvirt_domain.worker.network_interface[0].addresses[0]}

  [db]
  db ansible_host=${libvirt_domain.db.network_interface[0].addresses[0]}
  EOT
}
