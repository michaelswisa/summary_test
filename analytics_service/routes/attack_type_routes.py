from flask import Blueprint, jsonify, request
from analytics_service.services.attack_type_service import fetch_top_attack_types

attack_type_bp = Blueprint('attack_types', __name__)


@attack_type_bp.route('/top_attack_types', methods=['GET'])
def top_attack_types():
    top_n = request.args.get('top_n', type=int)
    result = fetch_top_attack_types(top_n)
    return jsonify(result)
