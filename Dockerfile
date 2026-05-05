FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/

WORKDIR /app

COPY pyproject.toml uv.lock /app/

RUN uv sync --frozen --no-install-project --no-dev

COPY . /app

CMD ["uv", "run", "--no-sync", "python", "main.py"]
