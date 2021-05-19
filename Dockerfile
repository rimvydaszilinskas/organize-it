FROM python:alpine

RUN mkdir /code
WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install --upgrade pip

COPY ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

COPY . /code/

CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "core.wsgi:application"]
