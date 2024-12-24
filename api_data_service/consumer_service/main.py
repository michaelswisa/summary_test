import json
import logging
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from api_data_service.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC
from api_data_service.consumer_service.services.processing_service import process_article
from api_data_service.database_mongo.db_connection import MongoDBConnection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_consumer():
    try:
        return KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='news_processing_group'
        )
    except Exception as e:
        logger.error(f"Failed to create Kafka consumer: {e}")
        raise

def main():
    consumer = create_consumer()
    db = MongoDBConnection()

    try:
        logger.info(f"Starting to consume messages from topic {KAFKA_TOPIC}")
        for message in consumer:
            try:
                article = message.value
                process_article(article, db)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                continue

    except KeyboardInterrupt:
        logger.info("Shutting down consumer gracefully...")
    finally:
        consumer.close()
        logger.info("Consumer closed")

if __name__ == "__main__":
    main() 