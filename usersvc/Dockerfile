FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry==1.8.3

# Copy source code BEFORE poetry install
COPY pyproject.toml poetry.lock* ./
COPY src ./src

# Now run install (it will find the package in src/usersvc)
RUN poetry install --no-interaction --no-ansi

EXPOSE 50052
CMD ["poetry", "run", "python", "src/usersvc/server.py"]
