from flask import Blueprint, render_template, request
from analytics_service.services.region_casualties_service import get_region_casualties_map
import os

map_bp = Blueprint('map', __name__, url_prefix='/maps')


@map_bp.route('/casualties-by-region', methods=['GET', 'POST'])
def show_casualties_map():
    top_n = request.form.get('top_n', type=int, default=None)
    map_path = os.path.join("templates", "casualties_map.html")

    map = get_region_casualties_map(top_n)
    map.save(map_path)

    return render_template("casualties_index.html")


@map_bp.route('/casualties-by-region/view')
def render_casualties_map():
    return render_template("casualties_map.html")
