from analytics_service.repository.analysis_repo import get_events_by_year_and_region


def calculate_percentage_change(prev_events, current_events):
    diff = abs(prev_events - current_events)
    if prev_events != 0:
        return diff, ((diff / prev_events) * 100)
    return diff, 0


def update_region_difference(region_differences, region_name, prev_year, year, diff, percentage_change):
    if region_name not in region_differences or percentage_change > region_differences[region_name][
        'percentage_change']:
        region_differences[region_name] = {
            'year_with_max_change': f"{prev_year}-{year}",
            'max_difference': diff,
            'percentage_change': percentage_change
        }


def format_results(region_differences, top_n=None):
    sorted_region_differences = sorted(region_differences.items(),
                                       key=lambda x: x[1]['percentage_change'],
                                       reverse=True)

    if top_n:
        sorted_region_differences = sorted_region_differences[:top_n]

    return [
        {
            "region_name": region,
            "year_with_max_change": data['year_with_max_change'],
            "max_difference": data['max_difference'],
            "percentage_change": round(data['percentage_change'], 2)
        }
        for region, data in sorted_region_differences
    ]


def process_region_differences(top_n=None):
    events_by_year_and_region = get_events_by_year_and_region()
    region_differences = {}
    previous_year_events = {}

    for row in events_by_year_and_region:
        region_name = row.region_name
        year = row.year
        total_events = row.total_events

        if region_name in previous_year_events:
            prev_year, prev_events = previous_year_events[region_name]
            diff, percentage_change = calculate_percentage_change(prev_events, total_events)
            update_region_difference(region_differences, region_name, prev_year, year, diff, percentage_change)

        previous_year_events[region_name] = (year, total_events)

    return format_results(region_differences, top_n)
