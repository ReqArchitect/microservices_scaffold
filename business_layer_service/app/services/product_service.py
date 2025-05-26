from typing import Any, Dict, Optional, Tuple, List
from ..models import Product, db

class ProductService:
    """
    Service layer for Product entity.
    """
    @staticmethod
    def create(data: Dict[str, Any]) -> Tuple[bool, str, Optional[Product]]:
        if not data.get('name'):
            return False, 'Name is required', None
        product = Product(**data)
        db.session.add(product)
        db.session.commit()
        return True, 'Product created', product

    @staticmethod
    def get(product_id: int) -> Optional[Product]:
        return Product.query.get(product_id)

    @staticmethod
    def update(product_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Optional[Product]]:
        product = Product.query.get(product_id)
        if not product:
            return False, 'Product not found', None
        for field in ['name', 'description']:
            if field in data:
                setattr(product, field, data[field])
        db.session.commit()
        return True, 'Product updated', product

    @staticmethod
    def delete(product_id: int) -> bool:
        product = Product.query.get(product_id)
        if not product:
            return False
        db.session.delete(product)
        db.session.commit()
        return True

    @staticmethod
    def list() -> List[Product]:
        return Product.query.all() 