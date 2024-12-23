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
            (func.coalesce(func.sum(Event.killed), 0) + func.coalesce(func.sum(Event.wounded), 0)).label(
                'total_casualties')
        ).join(Event).group_by(Group.name).order_by(
            (func.coalesce(func.sum(Event.killed), 0) + func.coalesce(func.sum(Event.wounded), 0)).desc())

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


# query 8
def active_groups_by_region(region_name=None, limit=5):
    session = get_session()
    try:
        query = session.query(
            Group.name.label('group_name'),
            func.count(Event.id).label('event_count')
        ) \
            .join(Event, Group.id == Event.group_id) \
            .join(City, Event.city_id == City.id) \
            .join(Country, City.country_id == Country.id) \
            .join(Region, Country.region_id == Region.id)

        if region_name:
            query = query.filter(Region.name == region_name)

        active_groups = query.group_by(Group.name) \
            .order_by(func.count(Event.id).desc()) \
            .limit(limit) \
            .all()

        return active_groups

    finally:
        session.close()


def get_shared_targets_by_groups(region_name=None, country_name=None):
    session = get_session()
    try:
        query = session.query(
            Event.target_type.label('target_type'),
            Group.name.label('group_name'),
            func.count(Event.id).label('event_count')
        ).select_from(Event) \
            .join(Group, Event.group_id == Group.id) \
            .join(City, Event.city_id == City.id) \
            .join(Country, City.country_id == Country.id)

        if region_name:
            query = query.join(Region, Country.region_id == Region.id).filter(Region.name == region_name)
        if country_name:
            query = query.filter(Country.name == country_name)

        query = query.group_by(Event.target_type, Group.name) \
            .having(func.count(Event.id) >= 1)

        data = query.all()

        targets_dict = {}
        for row in data:
            target_type = "Civilian Targets" if row.target_type else "Military/Government Targets"
            if target_type not in targets_dict:
                targets_dict[target_type] = {
                    "target_type": target_type,
                    "groups": []
                }
            targets_dict[target_type]["groups"].append({
                "name": row.group_name,
                "attacks": row.event_count
            })

        for target_data in targets_dict.values():
            target_data["groups"] = sorted(
                target_data["groups"],
                key=lambda x: x["attacks"],
                reverse=True
            )

        return sorted(
            targets_dict.values(),
            key=lambda x: len(x["groups"]),
            reverse=True
        )

    finally:
        session.close()
