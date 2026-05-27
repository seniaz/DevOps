# Міні-звіт: Лабораторна робота №3 — CI/CD

**Студент:** Клеценко Оксана, ІМ-42  
**Номер у списку:** 14  
**Репозиторій:** https://github.com/seniaz/DevOps

---

## 1. PR, успішно злитий після проходження перевірок

PR #1 — (Lab 3) Add CI/CD documentation to README

CI checks пройшли успішно (Code Analysis ✅, Tests ✅), merge дозволений.

![Успішний PR](/docs/screenshots/pr_s_1.png)

---

## 2. PR, що не може бути злитий (failed checks)

PR #2 — (Lab 3) Broken test for demo

Tests ❌ (Required) — тест `test_intentionally_broken` падає навмисно.  
Code Analysis ✅. Merge заблокований branch protection rules.

![Неуспішний PR](/docs/screenshots/pr_u_2.png)

---

## 3. Успішне розгортання + успішна верифікація

Tag: v1.0.23  
CD workflow: Build & Push Image ✅ → Deploy to Target Node ✅ → Verify Deployment ✅

![Успішний deploy](/docs/screenshots/verify_s.png)

---

## 4. Успішне розгортання + неуспішна верифікація

Tag: v1.0.24

Для демонстрації було зупинено nginx на target node (`sudo systemctl stop nginx`).  
Deploy пройшов успішно, Verify впав на перевірці nginx.

![Неуспішна верифікація](/docs/screenshots/verify_u.png)

---

## 5. Звіт по покриттю коду тестами

Coverage report завантажується як artifact при кожному push в main.

![Coverage report](/docs/screenshots/coverage.png)

---

## Конфігурація

| Компонент       | Деталі                                           |
| --------------- | ------------------------------------------------ |
| CI runner       | GitHub-hosted `ubuntu-latest`                    |
| CD runner       | Self-hosted на Ubuntu 24.04 VM (VirtualBox)      |
| Target node     | Ubuntu 24.04 VM (VirtualBox), IP: 192.168.56.107 |
| Docker registry | `ghcr.io/seniaz/devops`                          |
| База даних      | MariaDB 10.11, порт 3306                         |
| Застосунок      | Simple Inventory, порт 5000                      |

## Інфраструктура CI/CD

- **CI** (на кожен push/PR/tag): flake8, hadolint, shellcheck, yamllint, pytest + coverage ≥ 40%
- **CD** (на annotated tags): Docker build → GHCR push → SSH deploy → verify
- **Branch protection**: merge в main заблокований без проходження Code Analysis та Tests
