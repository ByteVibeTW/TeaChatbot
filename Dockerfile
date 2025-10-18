FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安裝 uv 並移到 PATH
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/

WORKDIR /app

COPY . /app

CMD ["sh", "-c","if [ ! -d .venv ]; then uv sync --frozen --no-cache-dir; fi && uv run python main.py"]
