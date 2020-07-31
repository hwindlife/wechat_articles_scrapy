import json

from kafka import KafkaProducer
from scrapy.utils.project import get_project_settings


class WxArticlePrd:
    settings = get_project_settings()
    producer = KafkaProducer(bootstrap_servers=settings.get("KAFKA_BROKERS"))
    topic = settings.get("KAFKA_WXARTICLE_TOPIC")

    def __init__(self):
        pass

    @classmethod
    def send_msg(cls, mess):
        mess = json.dumps(mess) if isinstance(mess, dict) else mess
        cls.producer.send(cls.topic, bytes(mess, encoding="utf8"))
        cls.producer.flush()

    @classmethod
    def close(cls):
        cls.producer.close()


if __name__ == "__main__":
    wx_article_prd = WxArticlePrd()
    wx_article_prd.send_msg({"aaa": "aaa", "bbb": "bbb"})
