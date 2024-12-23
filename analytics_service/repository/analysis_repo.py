from analytics_service.database_postgres.db_connection import get_session
from analytics_service.models import AttackType, Region, City, Country, Group, TargetType
from analytics_service.models.event_model import Event
from sqlalchemy import func


# query 1: מחזירה את סוגי ההתקפה הקטלניים ביותר לפי מספר נפגעים (הרוג = 2 נקודות, פצוע = נקודה)
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


# query 2: מחזירה את ממוצע הנפגעים לפי אזור גיאוגרפי
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


# query 3: מחזירה את הקבוצות עם מספר הנפגעים הגבוה ביותר
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


# query 6: מחזירה את מספר האירועים לפי שנה ואזור
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


# query 8: מחזירה את הקבוצות הפעילות ביותר באזור מסוים
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


# query 11: מזהה קבוצות שתוקפות מטרות משותפות באזור או מדינה מסוימים
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


# query 14: מזהה אזורים בהם קבוצות שונות משתמשות באותן שיטות תקיפה
def get_shared_attack_strategies_by_region():
    session = get_session()
    try:
        query = session.query(
            Region.name.label('region_name'),
            AttackType.name.label('attack_type'),
            Group.name.label('group_name')
        ).select_from(Event) \
            .join(AttackType, Event.attack_type_id == AttackType.id) \
            .join(Group, Event.group_id == Group.id) \
            .join(City, Event.city_id == City.id) \
            .join(Country, City.country_id == Country.id) \
            .join(Region, Country.region_id == Region.id)

        data = query.all()

        region_strategy_map = {}
        for row in data:
            if row.region_name not in region_strategy_map:
                region_strategy_map[row.region_name] = {}

            if row.attack_type not in region_strategy_map[row.region_name]:
                region_strategy_map[row.region_name][row.attack_type] = set()

            region_strategy_map[row.region_name][row.attack_type].add(row.group_name)

        results = {}
        for region, attack_types in region_strategy_map.items():
            shared_strategies = []
            for attack_type, groups in attack_types.items():
                if len(groups) > 1:
                    shared_strategies.append({
                        "attack_type": attack_type,
                        "groups": list(groups)
                    })

            if shared_strategies:
                results[region] = shared_strategies

        return results

    finally:
        session.close()


# query 15: מזהה קבוצות שתוקפות את אותם סוגי מטרות
def get_groups_with_similar_target_preferences():
    session = get_session()
    try:
        query = session.query(
            TargetType.name.label('target_type'),
            Group.name.label('group_name'),
            Event.year.label('year'),
            func.count(Event.id).label('attack_count')
        ).select_from(Event) \
            .join(Group, Event.group_id == Group.id) \
            .join(TargetType, Event.target_type_id == TargetType.id) \
            .group_by(TargetType.name, Group.name, Event.year) \
            .having(func.count(Event.id) >= 10)

        data = query.all()

        target_group_mapping = {}
        for row in data:
            if row.target_type not in target_group_mapping:
                target_group_mapping[row.target_type] = set()
            target_group_mapping[row.target_type].add(row.group_name)

        results = [
            {
                "target_type": target_type,
                "groups": list(groups)
            }
            for target_type, groups in target_group_mapping.items()
            if len(groups) > 1
        ]

        return sorted(results, key=lambda x: len(x["groups"]), reverse=True)

    finally:
        session.close()


# query 16: מזהה אזורים עם פעילות של מספר רב של קבוצות שונות
def get_high_intergroup_activity_areas():
    session = get_session()
    try:
        query = session.query(
            Country.name.label('country_name'),
            Group.name.label('group_name'),
            func.count(Event.id).label('event_count')
        ).select_from(Event) \
            .join(Group, Event.group_id == Group.id) \
            .join(City, Event.city_id == City.id) \
            .join(Country, City.country_id == Country.id) \
            .group_by(Country.name, Group.name) \
            .having(func.count(Event.id) >= 1)

        data = query.all()

        area_groups = {}
        for row in data:
            if row.country_name not in area_groups:
                area_groups[row.country_name] = set()
            area_groups[row.country_name].add(row.group_name)

        results = [
            {
                "country": country,
                "groups": list(groups),
                "total_groups": len(groups)
            }
            for country, groups in area_groups.items()
            if len(groups) > 1
        ]

        return sorted(results, key=lambda x: x["total_groups"], reverse=True)

    finally:
        session.close()


# query 19: מזהה קבוצות שתקפו מטרות זהות באותה שנה
def get_groups_with_same_targets_by_year():
    session = get_session()
    try:
        query = session.query(
            Event.year.label('year'),
            TargetType.name.label('target_type'),
            Group.name.label('group_name')
        ).select_from(Event) \
            .join(Group, Event.group_id == Group.id) \
            .join(TargetType, Event.target_type_id == TargetType.id) \
            .filter(Group.name.isnot(None))

        data = query.all()

        organized_data = {}
        for row in data:
            if row.year not in organized_data:
                organized_data[row.year] = {}
            if row.target_type not in organized_data[row.year]:
                organized_data[row.year][row.target_type] = set()

            organized_data[row.year][row.target_type].add(row.group_name)

        results = []
        for year in organized_data:
            year_data = {
                "year": year,
                "targets": []
            }

            for target_type, groups in organized_data[year].items():
                if len(groups) > 1:
                    year_data["targets"].append({
                        "target_type": target_type,
                        "groups": list(groups)
                    })

            if year_data["targets"]:
                results.append(year_data)

        return sorted(results, key=lambda x: x["year"])

    finally:
        session.close()
