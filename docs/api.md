# API — Simple Inventory

Усі ендпоінти, окрім кореневого, підтримують `Accept`-перемикання:

* `Accept: text/html` → проста HTML-сторінка (без JS, без CSS).
* `Accept: application/json` або будь-який інший → JSON.

Помилки повертаються у тому ж форматі, що й запит (`text/html` →
`<h1>404</h1>...`, інакше — `{"error": "...", "status": 404}`).

## `GET /`

Кореневий ендпоінт. Віддає **тільки** `text/html`. Якщо клієнт явно
вимагає інший тип (наприклад, `Accept: application/json`), повертається
`406 Not Acceptable`.

Тіло — HTML-таблиця з усіма бізнес-ендпоінтами.

```bash
curl -i http://<VM_IP>/
```

## `GET /health/alive`

Простий liveness-пробник. Завжди `200 OK`, тіло — `OK`.

```bash
curl -i http://127.0.0.1:5000/health/alive
```

> Ендпоінт **не** проксується назовні через nginx (доступний тільки
> локально, з самої VM).

## `GET /health/ready`

Readiness. Виконує `SELECT 1` до БД.

* OK → `200`, тіло `OK`.
* помилка → `500`, тіло, наприклад: `database unreachable: OperationalError`.

```bash
curl -i http://127.0.0.1:5000/health/ready
```

## `GET /items`

Список усіх предметів інвентарю — `id`, `name`.

```bash
# JSON
curl -H 'Accept: application/json' http://<VM_IP>/items
# [{"id": 1, "name": "screwdriver"}, ...]

# HTML
curl -H 'Accept: text/html' http://<VM_IP>/items
```

Відповідь HTML — таблиця з колонками ID, Name.

## `POST /items`

Створити предмет.

Параметри: `name` (рядок, обовʼязковий), `quantity` (ціле число, ≥ 0,
за замовчуванням `0`). Підтримуються:

* JSON body (`Content-Type: application/json`),
* form-encoded (`application/x-www-form-urlencoded`).

```bash
curl -i -H 'Content-Type: application/json' -H 'Accept: application/json' \
     -X POST -d '{"name":"hammer","quantity":3}' \
     http://<VM_IP>/items
# HTTP/1.1 201 Created
# {"id": 7, "name": "hammer", "quantity": 3, "created_at": "2026-05-11T12:34:56"}
```

Помилки:

* `400` — `name` відсутній / не рядок,
* `400` — `quantity` не ціле або від'ємне.

## `GET /items/<id>`

Деталі конкретного предмета.

```bash
curl -H 'Accept: application/json' http://<VM_IP>/items/7
# {"id": 7, "name": "hammer", "quantity": 3, "created_at": "2026-05-11T12:34:56"}
```

* `404` — якщо предмета з таким id немає.

## Схема таблиці

```sql
CREATE TABLE items (
    id         INT          NOT NULL AUTO_INCREMENT,
    name       VARCHAR(255) NOT NULL,
    quantity   INT          NOT NULL DEFAULT 0,
    created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_items_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

Створюється скриптом `app/migrate.py`, який також веде таблицю
`schema_version` для idempotent-міграцій.
