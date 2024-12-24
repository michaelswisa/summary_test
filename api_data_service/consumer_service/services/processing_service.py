import json
from api_data_service.services.api_services import classify_news_article, get_location

def process_article(article, db):
    if not isinstance(article, dict):
        print(f"Invalid article format: {article}")
        return

    body = article.get("body", "")
    if not body or not isinstance(body, str):
        print(f"Invalid or missing body: {body}")
        return

    try:
        classification = classify_news_article(body[:300])
        if not classification:
            return

        content = classification['choices'][0]['message']['content']
        parsed_content = json.loads(content)

        result = {
            'country': parsed_content.get('location', ''),
            'body': body,
            'category': parsed_content.get('classification', ''),
            'title': article.get('title', ''),
            'url': article.get('url', ''),
            'date': article.get('date', '')
        }

        location_ll = get_location(result['country'])
        result.update(location_ll)

        db.save_json_to_mongo(result)
        print(f"Successfully processed and saved article: {result.get('title', '')}")

    except Exception as e:
        print(f"Error processing article: {e}")
        return 