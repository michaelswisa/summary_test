from analytics_service.database_postgres.db_connection import get_session
from analytics_service.models import AttackType, Region, City, Country
from analytics_service.models.event_model import Event
from sqlalchemy import func


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

if __name__ == '__main__':
    print(get_average_casualties_by_region(top_n=5))