from analytics_service.repository.analysis_repo import get_average_casualties_by_region
import folium
from branca.colormap import LinearColormap
import json
import os

def get_region_coordinates():
    return {
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

def get_region_casualties_map(top_n=None):
    # קבלת הנתונים
    results = get_average_casualties_by_region(top_n)
    results_dict = {result.name: result.average_score for result in results}
    
    # ייפוי מדינות לאזורים
    country_to_region = {
        # Western Europe
        'FR': 'Western Europe', 'DE': 'Western Europe', 'GB': 'Western Europe',
        'IT': 'Western Europe', 'ES': 'Western Europe', 'PT': 'Western Europe',
        'BE': 'Western Europe', 'NL': 'Western Europe', 'LU': 'Western Europe',
        'CH': 'Western Europe', 'AT': 'Western Europe', 'IE': 'Western Europe',
        'IS': 'Western Europe', 'NO': 'Western Europe', 'SE': 'Western Europe',
        'FI': 'Western Europe', 'DK': 'Western Europe',
        
        # Eastern Europe
        'RU': 'Eastern Europe', 'UA': 'Eastern Europe', 'PL': 'Eastern Europe',
        'RO': 'Eastern Europe', 'CZ': 'Eastern Europe', 'HU': 'Eastern Europe',
        'SK': 'Eastern Europe', 'BY': 'Eastern Europe', 'MD': 'Eastern Europe',
        'BG': 'Eastern Europe', 'HR': 'Eastern Europe', 'RS': 'Eastern Europe',
        'BA': 'Eastern Europe', 'AL': 'Eastern Europe', 'MK': 'Eastern Europe',
        'EE': 'Eastern Europe', 'LV': 'Eastern Europe', 'LT': 'Eastern Europe',
        
        # North America
        'US': 'North America', 'CA': 'North America',
        
        # Central America & Caribbean
        'MX': 'Central America & Caribbean', 'GT': 'Central America & Caribbean',
        'BZ': 'Central America & Caribbean', 'SV': 'Central America & Caribbean',
        'HN': 'Central America & Caribbean', 'NI': 'Central America & Caribbean',
        'CR': 'Central America & Caribbean', 'PA': 'Central America & Caribbean',
        'CU': 'Central America & Caribbean', 'JM': 'Central America & Caribbean',
        'HT': 'Central America & Caribbean', 'DO': 'Central America & Caribbean',
        
        # South America
        'BR': 'South America', 'AR': 'South America', 'CL': 'South America',
        'UY': 'South America', 'PY': 'South America', 'BO': 'South America',
        'PE': 'South America', 'EC': 'South America', 'CO': 'South America',
        'VE': 'South America', 'GY': 'South America', 'SR': 'South America',
        
        # East Asia
        'CN': 'East Asia', 'JP': 'East Asia', 'KR': 'East Asia',
        'KP': 'East Asia', 'MN': 'East Asia', 'TW': 'East Asia',
        
        # Southeast Asia
        'ID': 'Southeast Asia', 'MY': 'Southeast Asia', 'PH': 'Southeast Asia',
        'VN': 'Southeast Asia', 'TH': 'Southeast Asia', 'MM': 'Southeast Asia',
        'KH': 'Southeast Asia', 'LA': 'Southeast Asia', 'SG': 'Southeast Asia',
        
        # South Asia
        'IN': 'South Asia', 'PK': 'South Asia', 'BD': 'South Asia',
        'NP': 'South Asia', 'LK': 'South Asia', 'BT': 'South Asia',
        'MV': 'South Asia',
        
        # Central Asia
        'KZ': 'Central Asia', 'UZ': 'Central Asia', 'TM': 'Central Asia',
        'KG': 'Central Asia', 'TJ': 'Central Asia',
        
        # Middle East & North Africa
        'SA': 'Middle East & North Africa', 'IR': 'Middle East & North Africa',
        'IQ': 'Middle East & North Africa', 'TR': 'Middle East & North Africa',
        'SY': 'Middle East & North Africa', 'JO': 'Middle East & North Africa',
        'IL': 'Middle East & North Africa', 'LB': 'Middle East & North Africa',
        'EG': 'Middle East & North Africa', 'LY': 'Middle East & North Africa',
        'TN': 'Middle East & North Africa', 'DZ': 'Middle East & North Africa',
        'MA': 'Middle East & North Africa', 'AE': 'Middle East & North Africa',
        'QA': 'Middle East & North Africa', 'BH': 'Middle East & North Africa',
        'KW': 'Middle East & North Africa', 'OM': 'Middle East & North Africa',
        'YE': 'Middle East & North Africa',
        
        # Sub-Saharan Africa
        'ZA': 'Sub-Saharan Africa', 'NG': 'Sub-Saharan Africa',
        'KE': 'Sub-Saharan Africa', 'ET': 'Sub-Saharan Africa',
        'CD': 'Sub-Saharan Africa', 'TZ': 'Sub-Saharan Africa',
        'UG': 'Sub-Saharan Africa', 'GH': 'Sub-Saharan Africa',
        'CM': 'Sub-Saharan Africa', 'CI': 'Sub-Saharan Africa',
        'MG': 'Sub-Saharan Africa', 'AO': 'Sub-Saharan Africa',
        'MZ': 'Sub-Saharan Africa', 'ZM': 'Sub-Saharan Africa',
        'ZW': 'Sub-Saharan Africa', 'SD': 'Sub-Saharan Africa',
        'ML': 'Sub-Saharan Africa', 'BF': 'Sub-Saharan Africa',
        'SN': 'Sub-Saharan Africa', 'SO': 'Sub-Saharan Africa',
        
        # Australasia & Oceania
        'AU': 'Australasia & Oceania', 'NZ': 'Australasia & Oceania',
        'PG': 'Australasia & Oceania', 'FJ': 'Australasia & Oceania'
    }
    
    # יצירת מפה בסיסית
    m = folium.Map(location=[20, 0], zoom_start=2)
    
    # חישוב ערכי מינימום ומקסימום לסקאלת הצבעים
    values = [result.average_score for result in results]
    min_value = min(values) if values else 0
    max_value = max(values) if values else 1
    
    # יצירת סקאלת צבעים
    colormap = LinearColormap(
        colors=['green', 'yellow', 'red'],
        vmin=min_value,
        vmax=max_value
    )

    def style_function(feature):
        country_code = feature['properties']['ISO_A2']
        region_name = country_to_region.get(country_code)
        
        if region_name and region_name in results_dict:
            return {
                'fillColor': colormap(results_dict[region_name]),
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.7
            }
        return {
            'fillColor': '#CCCCCC',
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.1
        }

    # קריאת קובץ ה-GeoJSON של המדינות
    geojson_path = os.path.join(os.path.dirname(__file__), 'data', 'countries.geojson')
    
    # הוספת שכבת ה-GeoJSON למפה
    folium.GeoJson(
        json.load(open(geojson_path, 'r', encoding='utf-8')),
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=['ADMIN', 'ISO_A2'],
            aliases=['Country:', 'Code:'],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    ).add_to(m)
    
    # הוספת מקרא
    colormap.add_to(m)
    
    return m 