from analytics_service.repository.analysis_repo import get_events_by_year_and_region
import folium
from branca.colormap import LinearColormap

def calculate_region_changes(top_n=None):
    events_data = get_events_by_year_and_region()
    
    # מיפוי הנתונים לפי אזור ושנה
    region_year_data = {}
    for event in events_data:
        if event.region_name not in region_year_data:
            region_year_data[event.region_name] = {}
        region_year_data[event.region_name][event.year] = event.total_events
    
    # חישוב השינוי המקסימלי עבור כל אזור
    region_changes = {}
    for region, year_data in region_year_data.items():
        years = sorted(year_data.keys())
        max_change = 0
        max_change_years = None
        
        for i in range(len(years)-1):
            current_year = years[i]
            next_year = years[i+1]
            
            current_events = year_data[current_year]
            next_events = year_data[next_year]
            
            if current_events > 0:  # מניעת חלוקה באפס
                change_percent = ((next_events - current_events) / current_events) * 100
                if abs(change_percent) > abs(max_change):
                    max_change = change_percent
                    max_change_years = (current_year, next_year)
        
        if max_change_years:
            region_changes[region] = {
                'change_percent': max_change,
                'years': max_change_years,
                'start_events': year_data[max_change_years[0]],
                'end_events': year_data[max_change_years[1]]
            }
    
    # מיון לפי אחוז השינוי המוחלט
    sorted_changes = sorted(region_changes.items(), 
                          key=lambda x: abs(x[1]['change_percent']), 
                          reverse=True)
    
    if top_n:
        sorted_changes = sorted_changes[:top_n]
        
    return dict(sorted_changes)

def create_change_map(changes):
    m = folium.Map(location=[20, 0], zoom_start=2)
    
    # יצירת סקאלת צבעים
    values = [abs(data['change_percent']) for data in changes.values()]
    max_value = max(values) if values else 100
    
    colormap = LinearColormap(
        colors=['green', 'yellow', 'red'],
        vmin=0,
        vmax=max_value
    )
    
    # הוספת פוליגונים לאזורים
    for region, data in changes.items():
        coordinates = get_region_coordinates(region)
        if coordinates:
            folium.Circle(
                location=coordinates,
                radius=200000,  # רדיוס במטרים
                popup=f"{region}<br>שינוי: {data['change_percent']:.2f}%<br>שנים: {data['years'][0]}-{data['years'][1]}",
                color='black',
                fill=True,
                fillColor=colormap(abs(data['change_percent'])),
                fillOpacity=0.7
            ).add_to(m)
    
    # הוספת מקרא
    colormap.add_to(m)
    
    return m

def get_region_coordinates(region):
    # מיקומים משוערים של מרכזי האזורים
    coordinates = {
        'Western Europe': [48.379433, 9.795731],
        'Eastern Europe': [54.525961, 25.255933],
        'North America': [48.379433, -100.795731],
        'Central America & Caribbean': [23.634501, -102.552784],
        'South America': [-8.783195, -55.491477],
        'East Asia': [35.861660, 104.195397],
        'Southeast Asia': [4.210484, 101.975766],
        'South Asia': [20.593684, 78.962880],
        'Central Asia': [41.377491, 64.585262],
        'Middle East & North Africa': [29.311660, 47.481766],
        'Sub-Saharan Africa': [8.783195, 34.508523],
        'Australasia & Oceania': [-25.274398, 133.775136]
    }
    return coordinates.get(region) 