from loading_additional_data_source_service.clean_data import (
    load_data, clean_and_save_country, clean_and_save_city,
    clean_and_save_group, clean_and_save_attack_type, clean_and_save_event,
    convert_nan_to_none
)
from loading_additional_data_source_service.database_postgres.db_connection import get_session
from loading_additional_data_source_service.config import PATH_DATA_CSV_LOAD


def main():
    session = get_session()
    df = load_data(PATH_DATA_CSV_LOAD)
    
    for _, row in df.iterrows():
        try:
            row = convert_nan_to_none(row)
            country_id = clean_and_save_country(row['Country'], session)
            city_id = clean_and_save_city(row['City'], country_id, session)
            group_id = clean_and_save_group(row['Perpetrator'], session)
            attack_type_id = clean_and_save_attack_type(row['Weapon'], session)
            
            clean_and_save_event(
                row=row,
                city_id=city_id,
                group_id=group_id,
                attack_type_id=attack_type_id,
                session=session
            )
            
        except Exception as e:
            print(f"Error processing row: {e}")
            continue
    
    session.close()


if __name__ == "__main__":
    main() 