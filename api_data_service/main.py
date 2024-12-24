import json
import time
from api_data_service.database_mongo.db_connection import MongoDBConnection
from api_data_service.services.api_services import fetch_articles, classify_news_article, get_location


def process_article(article, db):
    body = article.get("body", "")
    if not body:
        return

    classification = classify_news_article(body[:300])
    if not classification:
        return

    content = classification['choices'][0]['message']['content']
    parsed_content = json.loads(content)

    result = {
        'country': parsed_content.get('location', ''),
        'body': body,
        'category': parsed_content.get('classification', '')
    }

    location_ll = get_location(result['country'])
    result.update(location_ll)

    db.save_json_to_mongo(result)


def main():
    db = MongoDBConnection()
    articles_page = 1

    while True:
        print(f"Fetching articles for page {articles_page}...")
        articles = fetch_articles(articles_page)

        if not articles:
            break

        results = articles.get("results", [])
        for article in results[:10]:
            process_article(article, db)

        articles_page += 1
        time.sleep(120)


if __name__ == "__main__":
    main()
