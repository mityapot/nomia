FROM python:3.12-alpine
ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1
RUN pip install --upgrade pip

ENV POETRY_VERSION=1.7.1
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' entrypoint.sh
RUN chmod +x entrypoint.sh

# Install dependencies
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-ansi --without dev

COPY . .
ENTRYPOINT ["/app/entrypoint.sh"]