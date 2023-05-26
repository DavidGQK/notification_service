import pika
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    EXCHANGE = Field('notifications')
    INSTANT_QUEUE = Field('instant_events')
    ROUTING_KEY = Field('instant_events')
    RABBIT_USER = Field('ugc_publisher')
    RABBIT_PASS = Field('qweqwe')
    RABBIT_HOST = Field('localhost')
    kafka_url: str = Field('localhost:9092')
    kafka_client: str = Field('kafka-movies-api')
    topic_list: list = Field(['views'])
    project_name: str = Field('ugc_movies_api')
    mongo_db: str = Field('views')
    mongo_url: str = Field('mongodb://127.0.0.1:27017')
    sentry_dns: str = Field(...)
    logstash_host: str = Field(...)
    logstash_port: int = Field(...)
    log_level: str = Field('INFO')
    
    notif_api_url: str = Field('http://api_notif:8201')

    class Config:
        env_file = '../.env'


settings = Settings()
kafka_list_urls = [settings.kafka_url]

credentials = pika.PlainCredentials(username=settings.RABBIT_USER, password=settings.RABBIT_PASS)

def rabbit_conn(credentials=credentials):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBIT_HOST, credentials=credentials))
    return connection
