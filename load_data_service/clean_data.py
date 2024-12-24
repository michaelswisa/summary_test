import pandas as pd
from load_data_service.models.attack_type_model import AttackType
from load_data_service.models.city_model import City
from load_data_service.models.country_model import Country
from load_data_service.models.event_model import Event
from load_data_service.models.group_model import Group
from load_data_service.models.region_model import Region
from load_data_service.models.target_type_model import TargetType

required_columns = ['iyear', 'imonth', 'iday', 'latitude', 'longitude', 'summary', 'gname', 'attacktype1', 'nperps',
                    'attacktype1_txt', 'targtype1', 'targtype1_txt', 'nkill', 'nwound', 'region', 'region_txt',
                    'country', 'country_txt', 'city'
                    ]


def load_data(path):
    df = pd.read_csv(path,
                     encoding='latin1',
                     usecols=required_columns)

    return df


def clean_and_save_region(row, session):
    region = session.query(Region).filter(Region.id == int(row['region'])).first()

    if not region:
        region = Region(
            id=int(row['region']),
            name=row['region_txt']
        )

        session.add(region)
        session.commit()
        session.refresh(region)

    return region.id


def clean_and_save_country(row, region_id, session):
    country = session.query(Country).filter(Country.id == row['country']).first()

    if not country:
        country = Country(
            id=int(row['country']),
            name=row['country_txt'],
            region_id=region_id
        )

        session.add(country)
        session.commit()
        session.refresh(country)

    return country.id


def clean_and_save_city(row, country_id, session):
    city = session.query(City).filter_by(name=row['city'], country_id=country_id).first()

    if not city:
        city = City(
            name=row['city'],
            country_id=country_id,
        )

        session.add(city)
        session.commit()
        session.refresh(city)

    return city.id


def clean_and_save_attack_type(row, session):
    attack_type = session.query(AttackType).filter(AttackType.id == row['attacktype1']).first()

    if not attack_type:
        attack_type = AttackType(
            id=int(row['attacktype1']),
            name=row['attacktype1_txt']
        )
        session.add(attack_type)
        session.commit()
        session.refresh(attack_type)

    return attack_type.id


def clean_and_save_target_type(row, session):
    target_type = session.query(TargetType).filter(TargetType.id == row['targtype1']).first()

    if not target_type:
        target_type = TargetType(
            id=int(row['targtype1']),
            name=row['targtype1_txt']
        )
        session.add(target_type)
        session.commit()
        session.refresh(target_type)

    return target_type.id


def clean_and_save_group(row, session):
    group = session.query(Group).filter(Group.name == row['gname']).first()

    if not group:
        group = Group(
            name=row['gname']
        )
        session.add(group)
        session.commit()
        session.refresh(group)

    return group.id


def clean_and_save_event(row, city_id, attack_type_id, target_type_id, group_id, session):
    if row['iyear'] <= 0:
        row['iyear'] = None

    if row['imonth'] <= 0:
        row['imonth'] = None

    if row['iday'] <= 0:
        row['iday'] = None

    if pd.isna(row['nkill']) or row['nkill'] < 0:
        row['nkill'] = None

    if pd.isna(row['nwound']) or row['nwound'] < 0:
        row['nwound'] = None

    if pd.isna(row['nperps']) or row['nperps'] < 0:
        row['nperps'] = None

    event = Event(
        year=int(row['iyear']) if pd.notna(row['iyear']) else None,
        month=int(row['imonth']) if pd.notna(row['imonth']) else None,
        day=int(row['iday']) if pd.notna(row['iday']) else None,
        latitude=float(row['latitude']) if pd.notna(row['latitude']) else None,
        longitude=float(row['longitude']) if pd.notna(row['longitude']) else None,
        summary=row['summary'] if pd.notna(row['summary']) else None,
        nperps=float(row['nperps']) if pd.notna(row['nperps']) else None,
        killed=float(row['nkill']) if pd.notna(row['nkill']) else None,
        wounded=float(row['nwound']) if pd.notna(row['nwound']) else None,
        group_id=group_id,
        attack_type_id=attack_type_id,
        target_type_id=target_type_id,
        city_id=city_id
    )
    session.add(event)
    session.commit()


def convert_nan_to_none(row):
    for column in row.index:
        if pd.isna(row[column]):
            row[column] = None

    return row