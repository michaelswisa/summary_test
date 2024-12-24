from fastapi import FastAPI, HTTPException
from elasticsearch import Elasticsearch
from sqlalchemy import create_engine
from pymongo import MongoClient
from typing import List

from .models import SearchResult, SearchParams, SearchResponse
from .config import (
    ELASTICSEARCH_HOST, ELASTICSEARCH_PORT,
    MONGO_HOST, MONGO_PORT, MONGO_USERNAME, MONGO_PASSWORD, MONGO_DB_NAME,
    POSTGRES_URL
)

app = FastAPI(title="Terror Events Search Service")

# Initialize connections
es = Elasticsearch([f'http://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}'])
mongo_client = MongoClient(f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}")
mongo_db = mongo_client[MONGO_DB_NAME]
pg_engine = create_engine(POSTGRES_URL)

@app.post("/search/keywords", response_model=SearchResponse)
async def search_all_sources(params: SearchParams):
    # Build the query
    query = {
        "query": {
            "bool": {
                "must": [
                    {"multi_match": {
                        "query": params.query,
                        "fields": ["title^2", "body", "summary"],  # title gets higher weight
                        "fuzziness": "AUTO"  # handle typos
                    }}
                ],
                "filter": []
            }
        },
        "aggs": {
            "categories": {
                "terms": {"field": "category"}
            },
            "sources": {
                "terms": {"field": "source"}
            },
            "timeline": {
                "date_histogram": {
                    "field": "date",
                    "calendar_interval": "month"
                }
            }
        }
    }

    # Add filters
    if params.start_date or params.end_date:
        date_filter = {"range": {"date": {}}}
        if params.start_date:
            date_filter["range"]["date"]["gte"] = params.start_date.isoformat()
        if params.end_date:
            date_filter["range"]["date"]["lte"] = params.end_date.isoformat()
        query["query"]["bool"]["filter"].append(date_filter)

    if params.source:
        query["query"]["bool"]["filter"].append({"term": {"source": params.source}})

    if params.category:
        query["query"]["bool"]["filter"].append({"term": {"category": params.category}})

    if params.geo_filter:
        query["query"]["bool"]["filter"].append({
            "geo_distance": {
                "distance": params.geo_filter.distance,
                "location": {
                    "lat": params.geo_filter.lat,
                    "lon": params.geo_filter.lon
                }
            }
        })

    # Add sorting
    if params.sort_by:
        sort_config = []
        if params.sort_by == "date":
            sort_config.append({"date": {"order": params.sort_order or "desc"}})
        sort_config.append("_score")  # Always include relevance as secondary sort
        query["sort"] = sort_config

    # Execute search
    response = es.search(
        index="terror_events",
        body=query,
        size=params.limit
    )

    # Process results
    results = []
    for hit in response["hits"]["hits"]:
        source = hit["_source"]
        results.append(
            SearchResult(
                id=hit["_id"],
                title=source.get("title"),
                body=source.get("body") or source.get("summary"),
                date=source.get("date"),
                location={"lat": source.get("lat"), "lon": source.get("lon")} 
                    if source.get("lat") and source.get("lon") else None,
                source=source.get("source"),
                category=source.get("category"),
                score=hit["_score"]
            )
        )

    return SearchResponse(
        total=response["hits"]["total"]["value"],
        results=results,
        aggregations=response.get("aggregations")
    )

@app.post("/search/news", response_model=SearchResponse)
async def search_news(params: SearchParams):
    params.source = "news"
    return await search_all_sources(params)

@app.post("/search/historic", response_model=SearchResponse)
async def search_historic(params: SearchParams):
    params.source = "historic"
    return await search_all_sources(params)

@app.post("/search/combined", response_model=SearchResponse)
async def search_combined(params: SearchParams):
    return await search_all_sources(params)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 