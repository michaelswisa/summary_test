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
