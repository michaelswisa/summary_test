# Elasticsearch Configuration
ELASTICSEARCH_HOST = "localhost"
ELASTICSEARCH_PORT = 9200

# MongoDB Configuration
MONGO_HOST = 'localhost'
MONGO_PORT = 27018
MONGO_USERNAME = 'root'
MONGO_PASSWORD = 'example'
MONGO_DB_NAME = 'terror_events'

# PostgreSQL Configuration
POSTGRES_HOST = 'localhost'
POSTGRES_PORT = '5433'
POSTGRES_USER = 'postgres'
POSTGRES_PASSWORD = 'postgres'
POSTGRES_DB = 'terror_events'
POSTGRES_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}" 