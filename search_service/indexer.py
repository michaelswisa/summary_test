from elasticsearch import Elasticsearch, helpers
from sqlalchemy import create_engine, text
from pymongo import MongoClient
from datetime import datetime
from search_service.config import (
    ELASTICSEARCH_HOST, ELASTICSEARCH_PORT,
    MONGO_HOST, MONGO_PORT, MONGO_USERNAME, MONGO_PASSWORD, MONGO_DB_NAME,
    POSTGRES_URL
)

def create_index(es):
    index_body = {
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                "body": {"type": "text"},
                "summary": {"type": "text"},
                "date": {"type": "date"},
                "location": {"type": "geo_point"},
                "source": {"type": "keyword"},
                "category": {"type": "keyword"}
            }
        }
    }
    
    if not es.indices.exists(index="terror_events"):
        es.indices.create(index="terror_events", body=index_body)

def index_postgres_data(es, pg_engine):
    query = text("""
        SELECT e.id, e.summary, e.year, e.month, e.day, 
               e.latitude, e.longitude, 'historic' as source,
               at.name as category
        FROM events e
        LEFT JOIN attack_types at ON e.attack_type_id = at.id
    """)
    
    with pg_engine.connect() as conn:
        results = conn.execute(query)
        
        actions = []
        for row in results:
            date = None
            if row.year:
                try:
                    date = datetime(row.year, row.month or 1, row.day or 1)
                except ValueError:
                    pass
                    
            doc = {
                "_index": "terror_events",
                "_source": {
                    "summary": row.summary,
                    "date": date.isoformat() if date else None,
                    "lat": float(row.latitude) if row.latitude else None,
                    "lon": float(row.longitude) if row.longitude else None,
                    "source": "historic",
                    "category": row.category
                }
            }
            actions.append(doc)
            
        helpers.bulk(es, actions)

def index_mongodb_data(es, mongo_db):
    collection = mongo_db.event_collection
    
    actions = []
    errors = []
    
    for doc in collection.find():
        try:
            # Convert date string to ISO format if exists
            date = doc.get("date")
            if isinstance(date, str):
                try:
                    # Parse the date string to datetime and back to ISO format
                    parsed_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                    date = parsed_date.isoformat()
                except ValueError as e:
                    print(f"Warning: Could not parse date {date}: {e}")
                    date = None
            
            # Validate lat/lon
            lat = doc.get("lat")
            lon = doc.get("lon")
            if lat is not None:
                try:
                    lat = float(lat)
                except (ValueError, TypeError):
                    print(f"Warning: Invalid latitude value: {lat}")
                    lat = None
            if lon is not None:
                try:
                    lon = float(lon)
                except (ValueError, TypeError):
                    print(f"Warning: Invalid longitude value: {lon}")
                    lon = None
            
            es_doc = {
                "_index": "terror_events",
                "_source": {
                    "title": doc.get("title", ""),
                    "body": doc.get("body", ""),
                    "date": date,
                    "lat": lat,
                    "lon": lon,
                    "source": "news",
                    "category": doc.get("category", "")
                }
            }
            
            # Remove None values
            es_doc["_source"] = {k: v for k, v in es_doc["_source"].items() if v is not None}
            
            actions.append(es_doc)
            
        except Exception as e:
            print(f"Error processing document {doc.get('_id')}: {e}")
            errors.append({"doc": doc, "error": str(e)})
    
    if actions:
        try:
            success, failed = helpers.bulk(es, actions, stats_only=True)
            print(f"Successfully indexed {success} documents")
            if failed:
                print(f"Failed to index {failed} documents")
        except Exception as e:
            print(f"Bulk indexing error: {e}")
    
    if errors:
        print(f"\nEncountered {len(errors)} errors during processing:")
        for error in errors:
            print(f"Document: {error['doc'].get('_id')}, Error: {error['error']}")

def main():
    es = Elasticsearch([f'http://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}'])
    pg_engine = create_engine(POSTGRES_URL)
    mongo_client = MongoClient(f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}")
    mongo_db = mongo_client[MONGO_DB_NAME]
    
    print("Creating index...")
    create_index(es)
    
    print("Indexing PostgreSQL data...")
    index_postgres_data(es, pg_engine)
    
    print("Indexing MongoDB data...")
    index_mongodb_data(es, mongo_db)
    
    print("Indexing complete!")

if __name__ == "__main__":
    main() 