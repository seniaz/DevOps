# DevOps

Цей репозиторій містить повний набір лабораторних робіт, виконаних у межах курсу **«Технології розгортання програмного забезпечення комп'ютерних систем»**.

**Виконала:** Клеценко Оксана
**Група:** ІМ-42
**Номер у списку групи:** 14

---

## Лабораторна робота №1 — Розгортання Web-сервісу з автоматизацією

Стек: Python 3.12.10 + Flask, MariaDB, nginx, systemd (з socket activation)

### Варіант індивідуального завдання

`N = 14`

| Формула        | Значення | Що означає                                                          |
| -------------- | -------- | ------------------------------------------------------------------- |
| `V2 = (N%2)+1` | **1**    | конфігурація через **аргументи командного рядка**, БД — **MariaDB** |
| `V3 = (N%3)+1` | **3**    | застосунок — **Simple Inventory** (облік обладнання)                |
| `V5 = (N%5)+1` | **5**    | порт застосунку — **5000**                                          |

📄 Документація: [Lab 1 Report](./docs/lab1_report.md)

---

## Лабораторна робота №2 — Контейнеризація (Docker)

Дослідження контейнеризації на базі Python-проєкту: написання Dockerfile, оптимізація образу, робота з Docker CLI.

📄 Документація: [Lab 2 Report](./docs/lab2.md)
📄 Звіт-дослідження: [REPORT.md](https://github.com/seniaz/deploy.lab-containers-starter-project-python/blob/lab2/REPORT.md)

---

## Лабораторна робота №3 — CI/CD

### CI Pipeline

Запускається автоматично на push в `main`, annotated tags та Pull Requests.

**Jobs:**

- **Code Analysis** — flake8, hadolint, shellcheck, yamllint
- **Tests** — pytest + coverage (мінімум 40%)

### CD Pipeline

Запускається на push в `main` (build) та annotated tags (build + deploy + verify).

**Docker образ:** `ghcr.io/<username>/devops`

**Тегування:**

- push в main: `latest`, `sha-<hash>`
- annotated tag: `stable`, `<tag>`

📄 Документація: [Lab 3 Report](./docs/lab3.md)  
Міні-звіт: [lab3_mini-report](./docs/lab3_mini_report)

---

## Лабораторна робота №4 — Оркестрація

Багатоконтейнерне розгортання застосунку.

📄 Документація: [README.md (окремий репозиторій)](https://github.com/seniaz/DevOps_4/blob/main/README.md)
