# Notification Service

## Description
  - The notification service sends messages to the user on certain events (coming from Auth and User Generated Content services).

## Stack
  - RabbitMQ, Kafka, ClickHouse, FastAPI, MongoDB, Mailhog, Flask, SQLAlchemy, Flask, aiohttp, Django

## Deploy
  - fill in `.env`
  - `docker-compose -f docker-compose-notif_new.yml up --build`

## Endpoints
  - http://127.0.0.1:5000/auth/docs/v1
  - http://127.0.0.1:8000/ugc/api/openapi
  - http://127.0.0.1:8082/notif/admin
  - http://127.0.0.1:15672/ ~ rabbit gui (admin/123456789)
  - http://127.0.0.1:8025/ ~ mailhog gui