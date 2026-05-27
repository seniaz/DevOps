terraform {
  required_version = ">= 1.5.0"

  required_providers {
    libvirt = {
      source  = "dmacvicar/libvirt"
      version = "~> 0.8.1"
    }
  }
}

provider "libvirt" {
  uri = var.libvirt_uri
}

resource "libvirt_network" "lab_network" {
  name      = "lab4-network"
  mode      = "nat"
  domain    = "lab4.local"
  autostart = true

  addresses = ["192.168.122.0/24"]

  dns {
    enabled = true
  }
}

resource "libvirt_volume" "ubuntu_base" {
  name   = "ubuntu-24.04-base.qcow2"
  pool   = var.storage_pool
  source = var.ubuntu_image_url
  format = "qcow2"
}

resource "libvirt_volume" "worker_disk" {
  name           = "worker.qcow2"
  pool           = var.storage_pool
  base_volume_id = libvirt_volume.ubuntu_base.id
  size           = var.worker_disk_size
  format         = "qcow2"
}

resource "libvirt_volume" "db_disk" {
  name           = "db.qcow2"
  pool           = var.storage_pool
  base_volume_id = libvirt_volume.ubuntu_base.id
  size           = var.db_disk_size
  format         = "qcow2"
}

resource "libvirt_cloudinit_disk" "worker_init" {
  name = "worker-init.iso"
  pool = var.storage_pool

  user_data = templatefile("${path.module}/cloud-init/worker.yml", {
    ssh_public_key = var.ssh_public_key
    hostname       = "worker"
  })
}

resource "libvirt_cloudinit_disk" "db_init" {
  name = "db-init.iso"
  pool = var.storage_pool

  user_data = templatefile("${path.module}/cloud-init/db.yml", {
    ssh_public_key = var.ssh_public_key
    hostname       = "db"
  })
}

resource "libvirt_domain" "worker" {
  name   = "lab4-worker"
  memory = var.worker_memory
  vcpu   = var.worker_vcpu

  cloudinit = libvirt_cloudinit_disk.worker_init.id

  network_interface {
    network_id     = libvirt_network.lab_network.id
    wait_for_lease = true
  }

  disk {
    volume_id = libvirt_volume.worker_disk.id
  }

  console {
    type        = "pty"
    target_type = "serial"
    target_port = "0"
  }

  graphics {
    type        = "vnc"
    listen_type = "address"
    autoport    = true
  }
}

resource "libvirt_domain" "db" {
  name   = "lab4-db"
  memory = var.db_memory
  vcpu   = var.db_vcpu

  cloudinit = libvirt_cloudinit_disk.db_init.id

  network_interface {
    network_id     = libvirt_network.lab_network.id
    wait_for_lease = true
  }

  disk {
    volume_id = libvirt_volume.db_disk.id
  }

  console {
    type        = "pty"
    target_type = "serial"
    target_port = "0"
  }

  graphics {
    type        = "vnc"
    listen_type = "address"
    autoport    = true
  }
}
