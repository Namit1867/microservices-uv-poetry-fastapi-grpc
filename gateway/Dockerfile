FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry==1.8.3

# Copy source code BEFORE poetry install
COPY pyproject.toml poetry.lock* ./
COPY src ./src

# Now run install (it will find the package in src/ordersvc)
RUN poetry install --no-interaction --no-ansi

EXPOSE 8080
CMD ["poetry", "run", "uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8080"]
