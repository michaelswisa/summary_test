import json
import requests
from api_data_service.config import (
    EVENT_REGISTRY_URL,
    GROQ_API_KEY,
    GROQ_API_URL,
    OPENCAGE_API_KEY,
    RESPONSE_FORMAT_GROQ
)


def fetch_articles(page):
    response = requests.get(f"{EVENT_REGISTRY_URL}{page}")
    if response.status_code == 200:
        return response.json().get('articles')
    else:
        print(f"Error fetching articles: {response.status_code}")
        return []


def classify_news_article(article_content):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    payload = {
        "messages": [
            {"role": "system",
             "content": "You are an assistant classifying news articles into categories and locations"},
            {"role": "user", "content": f"This is a news article: {article_content}"}
        ],
        "model": "grok-2-1212",
        "stream": False,
        "temperature": 0,
        "response_format": RESPONSE_FORMAT_GROQ
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError:
            print("Failed to decode JSON response")
            return None
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")
        return None


def get_location(name):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={name}&key={OPENCAGE_API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            location = data["results"][0]["geometry"]
            return {"lon": location["lng"], "lat": location["lat"]}
        else:
            print(f"No geolocation data found for {name}.")
            return {"lon": 0.0, "lat": 0.0}
    else:
        print(f"Error fetching geolocation data: {response.status_code}")
        return {"lon": 0.0, "lat": 0.0}
