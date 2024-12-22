from analytics_service.repository.analysis_repo import get_top_attack_types

def fetch_top_attack_types(top_n=None):
    results = get_top_attack_types(top_n)
    return [{'name': row.name, 'score': row.score} for row in results] 