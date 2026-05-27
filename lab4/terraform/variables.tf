variable "libvirt_uri" {
  description = "Libvirt connection URI"
  type        = string
  default     = "qemu:///system"
}

variable "storage_pool" {
  description = "Libvirt storage pool name"
  type        = string
  default     = "default"
}

variable "ubuntu_image_url" {
  description = "URL or local path to Ubuntu 24.04 cloud image"
  type        = string
  default     = "https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img"
}

variable "ssh_public_key" {
  description = "SSH public key for the ansible user"
  type        = string
}

variable "worker_memory" {
  description = "Worker VM RAM in MB"
  type        = number
  default     = 2048
}

variable "worker_vcpu" {
  description = "Worker VM CPU count"
  type        = number
  default     = 2
}

variable "worker_disk_size" {
  description = "Worker VM disk size in bytes"
  type        = number
  default     = 10737418240
}

variable "db_memory" {
  description = "DB VM RAM in MB"
  type        = number
  default     = 1024
}

variable "db_vcpu" {
  description = "DB VM CPU count"
  type        = number
  default     = 1
}

variable "db_disk_size" {
  description = "DB VM disk size in bytes"
  type        = number
  default     = 10737418240
}
