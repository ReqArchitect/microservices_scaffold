from .models import SearchQuery, db

class SearchService:
    @staticmethod
    def create_query(data):
        query = SearchQuery(**data)
        db.session.add(query)
        db.session.commit()
        return query

    @staticmethod
    def get_query(query_id):
        return SearchQuery.query.get(query_id)

    @staticmethod
    def get_queries(limit=10, offset=0):
        return SearchQuery.query.order_by(SearchQuery.created_at.desc()).limit(limit).offset(offset).all()

    @staticmethod
    def log_query(query, user_id=None, tenant_id=None, results=None):
        q = SearchQuery(query=query, user_id=user_id, tenant_id=tenant_id, results=results)
        db.session.add(q)
        db.session.commit()
        return q 