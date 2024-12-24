from flask import Blueprint, render_template, request
from analytics_service.services.region_change_service import calculate_region_changes, create_change_map
import os

region_change_bp = Blueprint('region_change', __name__, url_prefix='/region-change')

@region_change_bp.route('/', methods=['GET', 'POST'])
def show_region_changes():
    top_n = request.form.get('top_n', type=int, default=None)
    
    changes = calculate_region_changes(top_n)
    map_obj = create_change_map(changes)
    
    map_path = os.path.join("templates", "region_change_map.html")
    map_obj.save(map_path)
    
    return render_template("region_change_index.html", changes=changes)

@region_change_bp.route('/map')
def render_change_map():
    return render_template("region_change_map.html") 