from flask import Blueprint, request, jsonify
from .service import SearchService
from .schemas import SearchQuerySchema
from flasgger import swag_from
from datetime import datetime

search_bp = Blueprint('search', __name__, url_prefix='/api/v1/search')

@search_bp.route('/queries', methods=['POST'])
@swag_from({"summary": "Create search query", "responses": {201: {"description": "Created"}}})
def create_query():
    data = request.get_json()
    query = SearchService.create_query(data)
    return SearchQuerySchema().jsonify(query), 201

@search_bp.route('/queries/<int:query_id>', methods=['GET'])
@swag_from({"summary": "Get search query", "responses": {200: {"description": "OK"}, 404: {"description": "Not found"}}})
def get_query(query_id):
    query = SearchService.get_query(query_id)
    if not query:
        return jsonify({'message': 'Not found'}), 404
    return SearchQuerySchema().jsonify(query)

@search_bp.route('/queries', methods=['GET'])
@swag_from({"summary": "List search queries", "responses": {200: {"description": "OK"}}})
def get_queries():
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    queries = SearchService.get_queries(limit, offset)
    return SearchQuerySchema(many=True).jsonify(queries)

@search_bp.route('/log_query', methods=['POST'])
@swag_from({"summary": "Log query", "responses": {201: {"description": "Created"}}})
def log_query():
    data = request.get_json()
    query = SearchService.log_query(**data)
    return SearchQuerySchema().jsonify(query), 201

@search_bp.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "search-service", "timestamp": datetime.utcnow().isoformat()})

@search_bp.route('/metrics', methods=['GET'])
def metrics():
    # Dummy metrics
    return jsonify({"total_queries": len(SearchService.get_queries(1000, 0))}) 