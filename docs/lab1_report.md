# Лабораторна робота №1 — Розгортання Web-сервісу з автоматизацією

Студент: №14 у списку групи.
Стек: Python 3.12.10 + Flask, MariaDB, nginx, systemd (з socket activation),
Ubuntu 24.04 LTS.

## Варіант індивідуального завдання

`N = 14`

| Формула        | Значення | Що означає                                                          |
| -------------- | -------- | ------------------------------------------------------------------- |
| `V2 = (N%2)+1` | **1**    | конфігурація через **аргументи командного рядка**, БД — **MariaDB** |
| `V3 = (N%3)+1` | **3**    | застосунок — **Simple Inventory** (облік обладнання)                |
| `V5 = (N%5)+1` | **5**    | порт застосунку — **5000**                                          |

## Архітектура

```
client → nginx (0.0.0.0:80, reverse proxy)
              → mywebapp (127.0.0.1:5000)   socket-activated systemd unit
                    → MariaDB (127.0.0.1:3306)
```

- `nginx` віддає лише `/`, `/items`, `/items/<id>`. `/health/*` назовні приховані.
- `mywebapp` слухає `127.0.0.1` й отримує файловий дескриптор сокета
  від `systemd` через `LISTEN_FDS` (socket activation).
- MariaDB слухає лише `127.0.0.1`.

## Структура репозиторію

```
.
├── docs/
│   ├── api.md                 ← опис API
|   ├── lab1_report.md         ← звіт
│   └── deployment.md          ← деталі розгортання
├── app/
│   ├── mywebapp/              ← Python-пакет із застосунком
│   │   ├── __init__.py
│   │   ├── __main__.py        ← entrypoint: python -m mywebapp ...
│   │   ├── app.py             ← Flask + endpoints + content
|   |   |                        negotiation
│   │   ├── config.py          ← argparse → Config
│   │   ├── db.py              ← обгортка над PyMySQL
│   │   ├── server.py          ← WSGI + systemd socket activation
│   │   └── templates.py       ← HTML-шаблони (без JS/CSS)
│   ├── migrate.py             ← скрипт міграції БД (idempotent)
│   └── requirements.txt       ← закріплені залежності
└── deploy/
    ├── install.sh             ← єдина точка входу для автоматизації
    ├── scripts/               ← 7 кроків розгортання
    ├── systemd/               ← .service та .socket
    ├── nginx/                 ← конфіг reverse proxy
    └── sudoers/               ← права operator
```

## Опис застосунку

`Simple Inventory` — REST-сервіс обліку обладнання. Об'єкт інвентарю:
`id`, `name`, `quantity`, `created_at`.

Endpoints — див. [`api.md`](api.md). Стисло:

| Method | Path            | Призначення                                 |
| ------ | --------------- | ------------------------------------------- |
| GET    | `/`             | Список ендпоінтів бізнес-логіки (HTML only) |
| GET    | `/health/alive` | Liveness probe                              |
| GET    | `/health/ready` | Readiness probe (перевіряє з'єднання з БД)  |
| GET    | `/items`        | Список усіх предметів                       |
| POST   | `/items`        | Створити новий предмет                      |
| GET    | `/items/<id>`   | Деталі предмета                             |

API підтримує content negotiation: `Accept: text/html` → HTML,
будь-що інше → JSON. Кореневий ендпоінт віддає лише HTML.

## Як підняти середовище для розробки

```bash
git clone https://github.com/<you>/lab1.git
cd lab1/app
python3.12 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

# окрема локальна mariadb / sqlite не передбачена в проекті —
# для розробки можна швидко запустити mariadb у docker:
docker run --rm -d --name mariadb-dev \
    -e MARIADB_ROOT_PASSWORD=root \
    -e MARIADB_DATABASE=mywebapp \
    -e MARIADB_USER=mywebapp \
    -e MARIADB_PASSWORD=dev \
    -p 3306:3306 mariadb:11

python migrate.py --db-password dev
python -m mywebapp --port 5000 --db-password dev
```

Параметри застосунку — лише через CLI (V2=1):

```
python -m mywebapp --help
```

## Як розгорнути на ВМ

Детальна інструкція — [deployment.md](./deployment.md#5-тестування-розгорнутої-системи). Коротко:

1. Підняти ВМ з Ubuntu 24.04 Server (cloud image).
2. Залити репозиторій:

   ```bash
   sudo apt-get update && sudo apt-get install -y git
   git clone https://github.com/<you>/lab1.git /tmp/lab1
   cd /tmp/lab1
   chmod +x deploy/install.sh deploy/scripts/*.sh
   sudo ./deploy/install.sh
   ```

3. Готово. Перевірити:

   ```bash
   curl http://<VM_IP>/
   curl -H 'Accept: application/json' -X POST \
        -d '{"name":"screwdriver","quantity":3}' \
        -H 'Content-Type: application/json' http://<VM_IP>/items
   curl -H 'Accept: application/json' http://<VM_IP>/items
   ```

   Скрипт також створить `/home/student/gradebook` із `14`.

## Як тестувати розгорнуту систему

Див. [`docs/deployment.md` § Testing](docs/deployment.md#тестування-розгорнутої-системи).

## Користувачі

Створюються автоматично; пароль за замовчуванням `12345678`, потрібно
змінити при першому вході.

| Користувач | Призначення                  | Права                                |
| ---------- | ---------------------------- | ------------------------------------ |
| `student`  | особистий                    | в групі `sudo`                       |
| `teacher`  | для викладача                | в групі `sudo`                       |
| `operator` | експлуатація                 | sudo тільки на 5 команд (див. нижче) |
| `app`      | від нього стартує застосунок | системний, `nologin`                 |

`operator` через `sudo` може виконувати лише:

- `systemctl start|stop|restart|status mywebapp.service`
- `systemctl start|stop|restart|status mywebapp.socket`
- `systemctl reload nginx.service`

`ubuntu`/`debian`/`centos` за замовчуванням блокуються в кінці інсталяції.
