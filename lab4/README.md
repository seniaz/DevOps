# Лабораторна робота №4 — IaC: Terraform + Ansible

## Варіант (N = 14)

| Параметр | Формула | Значення | Опис |
|----------|---------|----------|------|
| V2 | (14 % 2) + 1 | **1** | Конфігурація через аргументи CLI, MariaDB |
| V3 | (14 % 3) + 1 | **3** | Simple Inventory |
| V5 | (14 % 5) + 1 | **5** | Порт 5000 |

## Архітектура

```
+---------VM1 (worker)----------+    +----VM2 (db)-----+
|  nginx:80 → mywebapp:5000     | →  |  MariaDB:3306   |
+-------------------------------+    +-----------------+
```

## Структура проєкту

```
lab4/
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── terraform.tfvars.example
│   └── cloud-init/
│       ├── worker.yml
│       └── db.yml
├── ansible/
│   ├── ansible.cfg
│   ├── playbook.yml
│   ├── inventory/
│   │   ├── hosts.ini
│   │   └── terraform_inventory.py
│   ├── group_vars/
│   │   ├── all.yml
│   │   ├── workers.yml
│   │   └── db.yml
│   └── roles/
│       ├── common/
│       ├── users/
│       ├── mariadb/
│       ├── webapp/
│       └── nginx/
└── README.md
```

## Передумови

- Linux-хост з KVM/QEMU та libvirt
- Terraform >= 1.5
- Ansible >= 2.15
- SSH-ключ

```bash
sudo apt install -y qemu-kvm libvirt-daemon-system virtinst
sudo apt install -y terraform ansible
ansible-galaxy collection install community.general community.mysql
ssh-keygen -t ed25519
```

## Запуск

### Terraform

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars

terraform init
terraform plan
terraform apply

terraform output worker_ip
terraform output db_ip
```

### Ansible

```bash
cd ../ansible
nano inventory/hosts.ini

ansible all -m ping
ansible-playbook playbook.yml
```

## Перевірка

```bash
WORKER_IP=$(cd ../terraform && terraform output -raw worker_ip)

curl http://$WORKER_IP/
curl http://$WORKER_IP/items
curl -X POST http://$WORKER_IP/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop", "quantity": 5}'
curl -H "Accept: application/json" http://$WORKER_IP/items/1
```

## Користувачі

| Користувач | ВМ | Права |
|---|---|---|
| ansible | Усі | sudo без пароля (cloud-init) |
| teacher | Усі | sudo з паролем (12345678 → зміна) |
| student | worker | sudo |
| app | worker | системний, мінімальні права |
| operator | worker | обмежений sudo |

## Знищення

```bash
cd terraform
terraform destroy
```
