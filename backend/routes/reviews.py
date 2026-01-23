"""
Review routes for CRUD operations
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models import models, schemas
from backend.utils.auth_utils import get_current_user

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])

@router.get("/")
async def get_all_reviews(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all reviews for current user with item details"""
    reviews = db.query(
        models.Review,
        models.Item.name.label('item_name')
    ).join(
        models.Item, models.Review.item_id == models.Item.id
    ).filter(
        models.Review.user_id == current_user.id
    ).order_by(
        models.Review.created_at.desc()
    ).all()
    
    return [
        {
            "id": review.Review.id,
            "item_id": review.Review.item_id,
            "item_name": review.item_name,
            "customer_name": review.Review.customer_name,
            "rating": float(review.Review.rating),
            "comment": review.Review.comment,
            "created_at": review.Review.created_at
        }
        for review in reviews
    ]

@router.get("/item/{item_id}")
async def get_reviews_by_item(
    item_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all reviews for a specific item"""
    # Verify item exists and belongs to user
    item = db.query(models.Item).filter(
        models.Item.id == item_id,
        models.Item.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    reviews = db.query(models.Review).filter(
        models.Review.item_id == item_id,
        models.Review.user_id == current_user.id
    ).order_by(
        models.Review.created_at.desc()
    ).all()
    
    return [
        {
            "id": review.id,
            "customer_name": review.customer_name,
            "rating": float(review.rating),
            "comment": review.comment,
            "created_at": review.created_at
        }
        for review in reviews
    ]

@router.get("/{review_id}", response_model=schemas.ReviewResponse)
async def get_review(
    review_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific review by ID"""
    review = db.query(models.Review).filter(
        models.Review.id == review_id,
        models.Review.user_id == current_user.id
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    return review

@router.post("/", response_model=schemas.ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: schemas.ReviewCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new review"""
    # Verify item exists
    item = db.query(models.Item).filter(
        models.Item.id == review_data.item_id,
        models.Item.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    new_review = models.Review(
        **review_data.dict(),
        user_id=current_user.id
    )
    
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    
    # Update item rating
    avg_rating = db.query(func.avg(models.Review.rating)).filter(
        models.Review.item_id == review_data.item_id
    ).scalar()
    
    if avg_rating:
        item.rating = round(float(avg_rating), 1)
        db.commit()
    
    return new_review

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a review"""
    review = db.query(models.Review).filter(
        models.Review.id == review_id,
        models.Review.user_id == current_user.id
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    item_id = review.item_id
    db.delete(review)
    db.commit()
    
    # Update item rating after deletion
    from sqlalchemy import func
    avg_rating = db.query(func.avg(models.Review.rating)).filter(
        models.Review.item_id == item_id
    ).scalar()
    
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if item:
        item.rating = round(float(avg_rating), 1) if avg_rating else 0.0
        db.commit()
    
    return None
