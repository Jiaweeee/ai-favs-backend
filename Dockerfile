FROM python:3.11-slim

# Install native dependencies
RUN apt-get update && apt-get install -y --fix-missing wget\
        curl\
        libglib2.0-0\
        libnss3\
        libnspr4\
        libdbus-1-3\
        libatk1.0-0\
        libatk-bridge2.0-0\
        libcups2\
        libatspi2.0-0\
        libx11-6\
        libxcomposite1\
        libxdamage1\
        libxext6\
        libxfixes3\
        libxrandr2\
        libgbm1\
        libdrm2\
        libxcb1\
        libxkbcommon0\
        libpango-1.0-0\
        libcairo2\
        libasound2

RUN pip install poetry==1.6.1

RUN poetry config virtualenvs.create false

WORKDIR /code

COPY ./pyproject.toml ./README.md ./poetry.lock* ./.env ./

COPY ./package[s] ./packages

RUN poetry install  --no-interaction --no-ansi --no-root

COPY ./app ./app

RUN poetry install --no-interaction --no-ansi

RUN playwright install chromium

EXPOSE 8080

CMD exec uvicorn app.server:app --host 0.0.0.0 --port ${PORT:-8080}
