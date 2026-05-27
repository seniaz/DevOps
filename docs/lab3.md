## Лабораторна робота №3 — CI/CD

### CI Pipeline

Автоматично запускається на кожен push в `main`, annotated tags `v*` та Pull Requests в `main`.

**Code Analysis:**

- `flake8` — лінтинг Python-коду (`app/mywebapp/`, `app/migrate.py`)
- `hadolint` — лінтинг `app/Dockerfile`
- `shellcheck` — лінтинг shell-скриптів (`deploy/scripts/`)
- `yamllint` — перевірка YAML файлів

**Tests:**

- `pytest` з MariaDB service container
- Покриття коду тестами ≥ 40%
- Звіт по покриттю завантажується як artifact

### CD Pipeline

Запускається на push в `main` (тільки build) та annotated tags (build + deploy + verify).

**Build & Push:**

- Збірка Docker образу з `app/Dockerfile`
- Публікація в GitHub Container Registry (`ghcr.io`)
- Теги: `latest` + `sha-<hash>` на push в main; `stable` + `<tag>` на annotated tags

**Deploy (тільки на теги):**

- Виконується на self-hosted runner
- SSH на target node → docker pull → migration → systemctl restart

**Verify (тільки на теги):**

- Health endpoints (`/health/alive`, `/health/ready`)
- Nginx reverse proxy (порт 80, блокування `/health`)
- Container status
- API функціональність (POST + GET `/items`)

### Branch Protection

Pull Requests в `main` вимагають проходження:

- Code Analysis
- Tests

### GitHub Secrets

| Secret            | Опис                                |
| ----------------- | ----------------------------------- |
| `SSH_PRIVATE_KEY` | SSH ключ для доступу до target node |
| `TARGET_HOST`     | IP-адреса target node               |
| `TARGET_USER`     | Користувач для SSH (`ansible`)      |
| `DB_PASSWORD`     | Пароль MariaDB                      |

### Запуск тестів локально

```bash
pip install -r app/requirements.txt
pip install pytest pytest-cov
# Запустити MariaDB в Docker, потім:
DB_HOST=127.0.0.1 DB_PORT=3306 DB_USER=testuser DB_PASSWORD=testpassword DB_NAME=testdb \
  pytest tests/ --cov=app/mywebapp --cov=app/migrate -v
```

### Розгортання

```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```
