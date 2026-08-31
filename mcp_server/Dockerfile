FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml .
COPY src ./src
COPY README.md .

RUN pip install .

CMD ["python", "-m", "mcp_server.main"]
