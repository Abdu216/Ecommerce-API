from typing import Optional
from pydantic import conint
from .base import BaseSchema, TimestampSchema
from .user import User


class ReviewBase(BaseSchema):
    product_id: int
    rating: conint(ge=1, le=5)  # Rating between 1 and 5
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseSchema):
    rating: Optional[conint(ge=1, le=5)] = None
    comment: Optional[str] = None


class Review(ReviewBase, TimestampSchema):
    id: int
    customer_id: int
    user_id: int
    is_verified_purchase: bool
    user: Optional[User] = None


# Response models for review operations
class ReviewStats(BaseSchema):
    average_rating: float
    total_reviews: int
    verified_reviews: int
    rating_distribution: dict[int, int]  # Distribution of ratings (1-5) 