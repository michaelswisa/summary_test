from analytics_service.database_postgres.db_connection import get_session
from analytics_service.models import AttackType, Region, City, Country, Group
from analytics_service.models.event_model import Event
from sqlalchemy import func


# query 1
def get_top_attack_types(top_n=None):
    session = get_session()
    try:
        query = session.query(
            AttackType.name,
            (func.sum(Event.killed) * 2 + func.sum(Event.wounded)).label('score')
        ).join(Event).group_by(AttackType.name).order_by(func.sum(Event.killed) * 2 + func.sum(Event.wounded).desc())

        if top_n:
            query = query.limit(top_n)

        return query.all()
    finally:
        session.close()


# query 2
def get_average_casualties_by_region(top_n=None):
    session = get_session()
    try:
        query = session.query(
            Region.name,
            (func.avg(Event.killed * 2 + Event.wounded)).label('average_score')
        ).join(City, Event.city_id == City.id) \
            .join(Country, City.country_id == Country.id) \
            .join(Region, Country.region_id == Region.id) \
            .group_by(Region.name) \
            .order_by(func.avg(Event.killed * 2 + Event.wounded).desc())

        if top_n:
            query = query.limit(top_n)

        return query.all()
    finally:
        session.close()


# query 3
def get_top_groups_by_casualties(top_n=None):
    session = get_session()
    try:
        query = session.query(
            Group.name,
            (func.sum(Event.killed) * 2 + func.sum(Event.wounded)).label('total_casualties')
        ).join(Event).group_by(Group.name).order_by(func.sum(Event.killed) * 2 + func.sum(Event.wounded).desc())

        if top_n:
            query = query.limit(top_n)

        return query.all()
    finally:
        session.close()


# query 6
def get_events_by_year_and_region():
    session = get_session()
    try:
        return session.query(
            Region.name.label('region_name'),
            Event.year.label('year'),
            func.count(Event.id).label('total_events')
        ) \
            .join(Country, Region.id == Country.region_id) \
            .join(City, Country.id == City.country_id) \
            .join(Event, City.id == Event.city_id) \
            .group_by(Region.name, Event.year) \
            .order_by(Region.name, Event.year) \
            .all()
    finally:
        session.close()
