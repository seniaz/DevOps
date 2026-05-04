# Розгортання

## 1. ВМ: базовий образ і ресурси

| Параметр       | Значення / рекомендація                                |
|----------------|--------------------------------------------------------|
| Дистрибутив    | **Ubuntu 24.04 LTS Server**                            |
| Образ          | Офіційний cloud-image: https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img |
| Архітектура    | `amd64` (`arm64` теж підійде, потрібно лише змінити образ) |
| vCPU           | 1                                                      |
| RAM            | 1 GiB                                                  |
| Disk           | 8 GiB (LVM не потрібен)                                |
| Партиціонування | За замовчуванням від cloud-image — без змін          |
| Networking     | NAT або bridged; потрібен зовнішній IP для перевірки   |

Якщо немає cloud-image — підійде ISO `ubuntu-24.04.x-live-server-amd64.iso`.
При інсталяції — guided storage, default user не важливий
(він буде заблокований автоматизацією).

### Доступ за SSH

* Для cloud-image: вхід за замовчуванням `ubuntu@<VM_IP>` з SSH-ключем,
  переданим через cloud-init.
* Для звичайної інсталяції — той користувач, якого ви створили в інсталяторі.
* Цей дефолтний користувач **блокується** в кроці 7 інсталяції
  (`usermod -L`, shell → `nologin`). Після цього входити треба як
  `student`, `teacher` або `operator` (пароль `12345678`, обов'язкова
  заміна при першому вході).

## 2. Підготовка та запуск

```bash
# 1. Зайдіть на ВМ (як default user, поки він не заблокований).
ssh ubuntu@<VM_IP>

# 2. Поставте git та клонуйте репозиторій.
sudo apt-get update -y
sudo apt-get install -y git
git clone https://github.com/<you>/lab1.git
cd lab1

# 3. Поставте exec-біт (на випадок, якщо він не зберігся в git).
chmod +x deploy/install.sh deploy/scripts/*.sh

# 4. Запуск.
sudo ./deploy/install.sh
```

### Корисні змінні оточення

* `STUDENT_NUMBER=14` — змусити перерахунок під інший варіант.
* `DB_PASSWORD=...`   — задати фіксований пароль до БД
  (інакше генерується випадковий `openssl rand -hex 16`).

```bash
sudo STUDENT_NUMBER=7 DB_PASSWORD='supersecret' ./deploy/install.sh
```

## 3. Що саме робить скрипт

| Крок | Файл                               | Дія |
|------|------------------------------------|-----|
| 1    | `scripts/01-packages.sh`           | apt-update, ставить deadsnakes PPA (python3.12.10), MariaDB, nginx |
| 2    | `scripts/02-users.sh`              | створює `student`, `teacher`, `operator`, `app`; вимикає first-login для людських |
| 3    | `scripts/03-database.sh`           | bind-address = 127.0.0.1; створює БД та користувача `mywebapp` |
| 4    | `scripts/04-app.sh`                | копіює код у `/opt/mywebapp`, створює venv, записує `/etc/mywebapp/env` (mode 640, owner root:app) |
| 5    | `scripts/05-systemd.sh`            | ставить `.service` + `.socket`, підставляє порт, `daemon-reload`, ставить `/etc/sudoers.d/operator` |
| 6    | `scripts/06-nginx.sh`              | заміна default-site, підставка порту, `nginx -t`, restart |
| 7    | `scripts/07-finalize.sh`           | `/home/student/gradebook`, блокування default user, перший warm-up curl |

Скрипти ідемпотентні — повторний запуск нічого не ламає.

## 4. systemd socket activation

`mywebapp.socket` слухає `127.0.0.1:5000` від імені `app:app` (mode `0600`).
Коли надходить перше з'єднання, systemd запускає `mywebapp.service`,
передаючи дескриптор сокета через `LISTEN_FDS=1` (FD 3). Наш
`mywebapp/server.py` зчитує цей FD через стандартний протокол
`SD_LISTEN_FDS_START = 3` і передає його у Werkzeug
(`make_server(host, port, app, fd=3)`).

`ExecStartPre=` запускає `migrate.py` перед стартом застосунку — це
гарантує, що схема БД підтягнута до останньої версії при кожному рестарті.

```bash
# Дивитись чи активований сокет:
systemctl status mywebapp.socket

# Журнал застосунку:
journalctl -u mywebapp.service -f

# Перевірити, що FD дійсно передається:
sudo strace -p $(pidof -s python3.12) -e trace=accept,read 2>&1 | head -20
```

## 5. Тестування розгорнутої системи

```bash
# 1. nginx живий і слухає :80
ss -ltnp | grep :80

# 2. mywebapp.socket слухає :5000 (тільки локально)
ss -ltnp | grep 127.0.0.1:5000

# 3. mariadb слухає тільки 127.0.0.1
ss -ltnp | grep 3306        # очікуємо 127.0.0.1:3306, не 0.0.0.0

# 4. Перевірка через nginx (як зовнішній клієнт)
curl -i http://<VM_IP>/
curl -i -H 'Accept: application/json' http://<VM_IP>/items
curl -i -X POST \
     -H 'Content-Type: application/json' -H 'Accept: application/json' \
     -d '{"name":"hammer","quantity":3}' http://<VM_IP>/items
curl -i -H 'Accept: application/json' http://<VM_IP>/items/1

# 5. Перевірка приховання /health/* через nginx (має бути 404)
curl -i http://<VM_IP>/health/alive
curl -i http://<VM_IP>/health/ready

# 6. Локально health-ендпоінти доступні
curl -i http://127.0.0.1:5000/health/alive
curl -i http://127.0.0.1:5000/health/ready

# 7. /home/student/gradebook існує і містить N
cat /home/student/gradebook                 # 14

# 8. Перевірка прав operator
# Sudo звіряє рядок команди ПОСИМВОЛЬНО з тим, що в /etc/sudoers.d/operator —
# тому `mywebapp.service` і `mywebapp` для sudo це різні команди. У файлі
# прописані повні форми з `.service` / `.socket`, їх і використовуємо.

# Дозволено (всі мають вийти з кодом 0):
sudo -u operator sudo -n systemctl start mywebapp.service   && echo OK
sudo -u operator sudo -n systemctl stop  mywebapp.service   && echo OK
sudo -u operator sudo -n systemctl restart mywebapp.service && echo OK
sudo -u operator sudo -n systemctl status mywebapp.service  && echo OK
sudo -u operator sudo -n systemctl reload  nginx.service    && echo OK

# Заборонено (всі мають видати "sudo: a password is required"):
sudo -u operator sudo -n systemctl restart nginx.service
sudo -u operator sudo -n systemctl restart mariadb.service
sudo -u operator sudo -n apt update
sudo -u operator sudo -n cat /etc/shadow

# 9. Default user заблокований
ssh ubuntu@<VM_IP>                          # має не пускати
```

## 6. Поширені проблеми

**`mywebapp.service: Failed at step EXEC ... No such file or directory`**
Сервіс не знайшов інтерпретатор у `/opt/mywebapp/venv/bin/python`.
Перевірте `04-app.sh` — можливо, не встановилось `python3.12-venv`.

**`pymysql.err.OperationalError: (2003, ...) Can't connect to MySQL server`**
MariaDB ще не встигла піднятись на момент запуску застосунку. Перевірте
`systemctl status mariadb`, а в `mywebapp.service` уже стоїть
`After=mariadb.service` + `Wants=mariadb.service`.

**`502 Bad Gateway` від nginx**
Сервіс не стартував. Перевірте `journalctl -u mywebapp.service`.
Найчастіша причина — порт у socket-unit ≠ порту в nginx upstream;
обидва підставляє `05-systemd.sh` і `06-nginx.sh` з єдиного `$APP_PORT`.

**`socket: Address already in use`** після зміни порту:
Сокет вже зайнятий старою чергою. `sudo systemctl restart mywebapp.socket`
очищує її; за потреби — `sudo systemctl stop mywebapp.socket && sleep 2 && start`.
