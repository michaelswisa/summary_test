from load_data_service.clean_data import *
from load_data_service.database_postgres.db_connection import get_session, init_db
from config import PATH_DATA_CSV_LOAD

def main():
    session = get_session()
    init_db()
    df = load_data(PATH_DATA_CSV_LOAD)
    for _, row in df.iterrows():
        row = convert_nan_to_none(row)
        region = clean_and_save_region(row, session)
        country = clean_and_save_country(row, region, session)
        city = clean_and_save_city(row, country, session)
        attack_type = clean_and_save_attack_type(row, session)
        target_type = clean_and_save_target_type(row, session)
        group = clean_and_save_group(row, session)
        clean_and_save_event(row, city, attack_type, target_type, group, session)

    session.close()


if __name__ == "__main__":
    main()