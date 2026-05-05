FROM python:3.13-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mywebapp/ mywebapp/
COPY migrate.py .

EXPOSE 5000

CMD ["sh", "-c", "python migrate.py --db-host db --db-port 3306 --db-user inventory --db-password inventory_pass --db-name inventory && python -m mywebapp --host 0.0.0.0 --port 5000 --db-host db --db-port 3306 --db-user inventory --db-password inventory_pass --db-name inventory"]