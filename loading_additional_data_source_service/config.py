PATH_DATA_CSV_LOAD=r'data\RAND_Database_of_Worldwide_Terrorism_Incidents - 5000 rows.csv'

POSTGRES_HOST = 'localhost'
POSTGRES_PORT = '5433'
POSTGRES_USER = 'postgres'
POSTGRES_PASSWORD = 'postgres'
POSTGRES_DB = 'terror_events'

POSTGRES_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
