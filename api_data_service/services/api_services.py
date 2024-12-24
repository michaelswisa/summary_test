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
    try:
        response = requests.get(f"{EVENT_REGISTRY_URL}{page}")
        print(f"API Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"API Response data: {json.dumps(data, indent=2)[:200]}...")  # Debug print
            
            # בבנה ה-JSON הוא nested - articles.results
            if "articles" in data and "results" in data["articles"]:
                return data["articles"]["results"]
            else:
                print(f"Unexpected API response structure. Keys found: {list(data.keys())}")
                return None
        else:
            print(f"Error fetching articles: {response.status_code}")
            print(f"Response content: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response: {e}")
        print(f"Response content: {response.text}")
        return None


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
