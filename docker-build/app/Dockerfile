FROM python:3.12.6-bookworm

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /src

RUN pip install --upgrade pip wheel "poetry==1.8.3"

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN poetry install

COPY src .

COPY ./src/alembic/versions /src/alembic/versions
COPY ./src/alembic.ini /src/alembic.ini

RUN chmod +x ./app/prestart.sh

ENTRYPOINT ["./app/prestart.sh"]
ENV PYTHONPATH=/src
CMD ["python", "./app/run.py"]
