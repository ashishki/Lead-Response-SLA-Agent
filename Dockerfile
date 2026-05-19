FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements-dev.txt pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "lead_sla_agent.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
