# MongoDB Configuration
MONGO_HOST = 'localhost'
MONGO_PORT = 27018
MONGO_USERNAME = 'root'
MONGO_PASSWORD = 'example'
MONGO_DB_NAME = 'terror_events'

# API Configuration
EVENT_REGISTRY_URL = "http://localhost:5000/articles?page="
GROQ_API_KEY = "xai-TI0fF0TQBLEcY4OUlakhjY5B29hKJiL313nGgFNn0NH0b4ee7HX5wyhfqHP9OAuu5puZ2nlAqGC2J4LX"
GROQ_API_URL = "https://api.x.ai/v1/chat/completions"
OPENCAGE_API_KEY = "bfa11842d84d477ebc17255c97c2cc3a"

# AI Response Format
RESPONSE_FORMAT_GROQ = {
    "type": "json_schema",
    "json_schema": {
        "name": "news_classification",
        "schema": {
            "type": "object",
            "properties": {
                "classification": {
                    "type": "string",
                    "enum": [
                        "Current terrorism event",
                        "Past terrorism event",
                        "Other news event"
                    ]
                },
                "location": {
                    "type": "string",
                    "description": "The location where the event occurred",
                    "longitude": "float",
                    "latitude": "float"
                }
            },
            "required": ["classification", "location"],
            "additionalProperties": False
        },
        "strict": True
    }
} 