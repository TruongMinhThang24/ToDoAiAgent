FROM python:3.13-slim 
RUN pip install poetry
WORKDIR /app

ENV PYTHONPATH="/app/src"


COPY pyproject.toml poetry.lock ./
RUN poetry  install --no-root --only main
COPY ./src ./src
EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
