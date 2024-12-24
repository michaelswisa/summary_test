import json
import time
import logging
from kafka import KafkaProducer
from kafka.errors import KafkaError
from api_data_service.services.api_services import fetch_articles
from api_data_service.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_producer():
    try:
        return KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            retries=5
        )
    except Exception as e:
        logger.error(f"Failed to create Kafka producer: {e}")
        raise

def main():
    producer = create_producer()
    articles_page = 1
    max_retries = 3

    try:
        while True:
            logger.info(f"\nFetching articles for page {articles_page}...")
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    articles = fetch_articles(articles_page)
                    if articles:
                        break
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.warning(f"Retry {retry_count}/{max_retries} in 30 seconds...")
                        time.sleep(30)
                except Exception as e:
                    logger.error(f"Error fetching articles: {e}")
                    retry_count += 1
                    if retry_count < max_retries:
                        time.sleep(30)
                    continue

            if not articles:
                logger.warning("No articles found after retries, moving to next page")
                articles_page += 1
                continue

            logger.info(f"Found {len(articles)} articles")
            for article in articles[:10]:
                if isinstance(article, dict) and article.get("body"):
                    try:
                        article_data = {
                            "body": article.get("body", ""),
                            "title": article.get("title", ""),
                            "url": article.get("url", ""),
                            "date": article.get("date", ""),
                            "source": article.get("source", "")
                        }
                        future = producer.send(KAFKA_TOPIC, article_data)
                        future.get(timeout=10)  # Wait for confirmation
                        logger.info(f"Sent article: {article_data.get('title', 'No title')[:50]}...")
                    except KafkaError as e:
                        logger.error(f"Failed to send article to Kafka: {e}")
                    except Exception as e:
                        logger.error(f"Unexpected error while processing article: {e}")

            articles_page += 1
            logger.info("Waiting 120 seconds before next fetch...")
            time.sleep(120)

    except KeyboardInterrupt:
        logger.info("Shutting down producer gracefully...")
    finally:
        producer.close()
        logger.info("Producer closed")

if __name__ == "__main__":
    main() 