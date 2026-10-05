FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace

COPY backend ./backend
COPY dbt ./dbt
COPY scripts ./scripts
COPY data ./data

RUN pip install --no-cache-dir -e "./backend" && \
    pip install --no-cache-dir -r dbt/requirements.txt

CMD ["python", "scripts/bootstrap_demo.py"]
