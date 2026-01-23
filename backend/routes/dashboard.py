"""
Dashboard routes for statistics and analytics
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal

from backend.database.connection import get_db
from backend.models import models, schemas
from backend.utils.auth_utils import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=schemas.DashboardStats)
async def get_dashboard_stats(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics - all data for admin dashboard"""
    
    # Total orders (all orders in the system)
    total_orders = db.query(func.count(models.Order.id)).scalar() or 0
    
    # Active orders (pending + new)
    active_orders = db.query(func.count(models.Order.id)).filter(
        models.Order.status.in_(['pending', 'new'])
    ).scalar() or 0
    
    # Orders to ship (preparing shipping status)
    to_ship = db.query(func.count(models.Shipping.id)).filter(
        models.Shipping.status == 'preparing'
    ).scalar() or 0
    
    # Total revenue (sum of paid payments)
    total_revenue = db.query(func.sum(models.Payment.amount)).filter(
        models.Payment.status == 'paid'
    ).scalar() or Decimal('0.00')
    
    # Total customers
    total_customers = db.query(func.count(models.Customer.id)).scalar() or 0
    
    # Total items
    total_items = db.query(func.count(models.Item.id)).scalar() or 0
    
    return {
        "total_orders": total_orders,
        "active_orders": active_orders,
        "to_ship": to_ship,
        "total_revenue": total_revenue,
        "total_customers": total_customers,
        "total_items": total_items
    }

@router.get("/top-items")
async def get_top_selling_items(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 5
):
    """Get top selling items - all items in the system for admin"""
    top_items = db.query(
        models.Item.name,
        func.count(models.Order.id).label('order_count')
    ).join(
        models.Order, models.Item.id == models.Order.item_id
    ).group_by(
        models.Item.id, models.Item.name
    ).order_by(
        func.count(models.Order.id).desc()
    ).limit(limit).all()
    
    return [{"name": item.name, "count": item.order_count} for item in top_items]

@router.get("/recent-reviews")
async def get_recent_reviews(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 5
):
    """Get recent customer reviews - all reviews for admin"""
    reviews = db.query(
        models.Review,
        models.Item.name.label('item_name')
    ).join(
        models.Item, models.Review.item_id == models.Item.id
    ).order_by(
        models.Review.created_at.desc()
    ).limit(limit).all()
    
    return [
        {
            "item_name": review.item_name,
            "customer_name": review.Review.customer_name,
            "rating": float(review.Review.rating),
            "comment": review.Review.comment,
            "created_at": review.Review.created_at
        }
        for review in reviews
    ]

@router.get("/average-rating")
async def get_average_rating(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get average rating across all reviews"""
    avg_rating = db.query(func.avg(models.Review.rating)).scalar()
    review_count = db.query(func.count(models.Review.id)).scalar() or 0
    
    return {
        "average_rating": round(float(avg_rating), 1) if avg_rating else 0.0,
        "review_count": review_count
    }
