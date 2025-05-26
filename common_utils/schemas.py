"""
Standardized API response schemas for ReqArchitect microservices.
"""
from typing import TypeVar, Generic, Optional, List, Dict, Any
from pydantic import BaseModel

T = TypeVar('T')

class PaginationMetadata(BaseModel):
    total_count: int
    page: int
    per_page: int
    total_pages: int

class ErrorDetail(BaseModel):
    code: str
    message: str
    field: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class BaseResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    errors: Optional[List[ErrorDetail]] = None
    pagination: Optional[PaginationMetadata] = None
    request_id: str

class ValidationError(BaseModel):
    loc: List[str]
    msg: str
    type: str

class HTTPValidationError(BaseModel):
    detail: List[ValidationError]
