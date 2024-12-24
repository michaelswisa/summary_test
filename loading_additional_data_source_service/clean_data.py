import pandas as pd
from loading_additional_data_source_service.models import (
    Country, City, Group, AttackType, Event, Region, TargetType
)
from loading_additional_data_source_service.database_postgres.db_connection import get_session
from sqlalchemy import func


def load_data(path):
    df = pd.read_csv(path,
                     encoding='latin1')

    return df


def parse_date(date_str):
    month_map = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }

    try:
        day, month_str, year_str = date_str.split('-')

        month = month_map[month_str]

        year = int(year_str)
        if year < 100:
            year = 1900 + year if year >= 25 else 2000 + year

        return {
            'year': year,
            'month': month,
            'day': int(day)
        }
    except (ValueError, KeyError) as e:
        return {
            'year': None,
            'month': None,
            'day': None
        }


def get_max_country_id():
    session = get_session()
    try:
        max_id = session.query(func.max(Country.id)).scalar()
        return max_id if max_id is not None else 0
    finally:
        session.close()


def clean_and_save_country(country_name, session=None):
    should_close_session = session is None
    if session is None:
        session = get_session()

    try:
        session.rollback()

        existing_country = session.query(Country).filter(Country.name == country_name).first()
        if existing_country:
            return existing_country.id

        max_id = get_max_country_id()
        new_id = max_id + 1

        new_country = Country(
            id=new_id,
            name=country_name
        )
        session.add(new_country)
        session.commit()

        return new_id

    except Exception as e:
        session.rollback()
        raise e

    finally:
        if should_close_session:
            session.close()


def clean_and_save_city(city_name, country_id, session=None):
    should_close_session = session is None
    if session is None:
        session = get_session()

    try:
        session.rollback()

        existing_city = session.query(City).filter(
            City.name == city_name,
            City.country_id == country_id
        ).first()

        if existing_city:
            return existing_city.id

        new_city = City(
            name=city_name,
            country_id=country_id
        )
        session.add(new_city)
        session.commit()
        session.refresh(new_city)

        return new_city.id

    except Exception as e:
        session.rollback()
        raise e

    finally:
        if should_close_session:
            session.close()


def clean_and_save_group(perpetrator_name, session=None):
    should_close_session = session is None
    if session is None:
        session = get_session()

    try:
        if not perpetrator_name or perpetrator_name == "Unknown":
            return None

        existing_group = session.query(Group).filter(Group.name == perpetrator_name).first()
        if existing_group:
            return existing_group.id

        new_group = Group(
            name=perpetrator_name
        )
        session.add(new_group)
        session.commit()
        session.refresh(new_group)

        return new_group.id

    finally:
        if should_close_session:
            session.close()


def get_max_attack_type_id():
    session = get_session()
    try:
        max_id = session.query(func.max(AttackType.id)).scalar()
        return max_id if max_id is not None else 0
    finally:
        session.close()


def clean_and_save_attack_type(weapon_name, session=None):
    should_close_session = session is None
    if session is None:
        session = get_session()

    try:
        existing_attack_type = session.query(AttackType).filter(AttackType.name == weapon_name).first()
        if existing_attack_type:
            return existing_attack_type.id

        max_id = get_max_attack_type_id()
        new_id = max_id + 1

        new_attack_type = AttackType(
            id=new_id,
            name=weapon_name
        )
        session.add(new_attack_type)
        session.commit()

        return new_id

    finally:
        if should_close_session:
            session.close()


def clean_and_save_event(row, city_id, group_id, attack_type_id, session=None):
    should_close_session = session is None
    if session is None:
        session = get_session()

    try:
        date_parts = parse_date(row['Date'])

        new_event = Event(
            summary=row['Description'],
            killed=row['Fatalities'] if pd.notna(row['Fatalities']) else None,
            wounded=row['Injuries'] if pd.notna(row['Injuries']) else None,
            group_id=group_id,
            attack_type_id=attack_type_id,
            city_id=city_id,
            year=date_parts['year'],
            month=date_parts['month'],
            day=date_parts['day']
        )

        session.add(new_event)
        session.commit()
        session.refresh(new_event)

        return new_event.id

    finally:
        if should_close_session:
            session.close()


def convert_nan_to_none(row):
    for column in row.index:
        if pd.isna(row[column]):
            row[column] = None

    return row
