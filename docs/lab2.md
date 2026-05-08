## Docker Compose (Лабораторна робота №2)

Контейнеризація всіх сервісів Simple Inventory за допомогою Docker Compose.

### Архітектура

```
client -> nginx (:80) -> webapp (:5000) -> MariaDB (:3306)
```

Усі сервіси працюють в ізольованій Docker-мережі `appnet`. Дані БД зберігаються в named volume `db_data` і переживають перезапуск контейнерів, Docker daemon та системи.

### Структура файлів

| Файл                         | Призначення                                         |
| ---------------------------- | --------------------------------------------------- |
| `docker-compose.yml`         | Оркестрація 3 сервісів                              |
| `app/Dockerfile`             | Образ веб-застосунку (python:3.13-slim-bookworm)    |
| `db/init.sql`                | Ініціалізація MariaDB (створення БД та користувача) |
| `nginx/docker.conf`          | Nginx reverse proxy для Docker-середовища           |
| `deploy/nginx/mywebapp.conf` | Nginx конфіг для ВМ (Лабораторна №1)                |

### Запуск

```bash
docker compose up -d --build
```

Перший запуск завантажує базові образи (~2-3 хв). Наступні — кілька секунд.

### Перевірка

```bash
docker compose ps
```

Має показати 3 контейнери зі статусом `Up`:

- `inventory-db` (healthy)
- `inventory-webapp`
- `inventory-nginx`

### Тестування API

```bash
# Головна сторінка
curl http://localhost/

# Створити запис
curl -X POST http://localhost/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop", "quantity": 10}'

# Список записів (JSON)
curl -H "Accept: application/json" http://localhost/items

# Деталі запису
curl -H "Accept: application/json" http://localhost/items/1
```

HTML-версія: відкрити `http://localhost/items` у браузері.

### Зупинка

```bash
docker compose down        # зберегти дані БД
docker compose down -v     # видалити все включно з даними
```

### Відмінності Docker vs ВМ

| Параметр      | ВМ (Лаб. №1)                 | Docker (Лаб. №2)          |
| ------------- | ---------------------------- | ------------------------- |
| Nginx конфіг  | `deploy/nginx/mywebapp.conf` | `nginx/docker.conf`       |
| Адреса webapp | `127.0.0.1:5000`             | `webapp:5000`             |
| Адреса БД     | `127.0.0.1:3306`             | `db:3306`                 |
| Міграція      | systemd ExecStartPre         | CMD в Dockerfile          |
| Конфігурація  | CLI args при запуску         | CLI args в Dockerfile CMD |
