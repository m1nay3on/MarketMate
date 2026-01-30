"""
Dashboard routes for statistics and analytics
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from decimal import Decimal
from datetime import datetime

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
    
    # Orders to ship (paid orders waiting to be shipped)
    to_ship = db.query(func.count(models.Order.id)).filter(
        models.Order.status == 'paid'
    ).scalar() or 0
    
    # Total revenue (sum of paid payments)
    total_revenue = db.query(func.sum(models.Payment.amount)).filter(
        models.Payment.status == 'paid'
    ).scalar() or Decimal('0.00')
    
    # Total customers
    total_customers = db.query(func.count(models.Customer.id)).scalar() or 0
    
    # Total active items (exclude deleted)
    total_items = db.query(func.count(models.Item.id)).filter(
        models.Item.is_deleted == 0
    ).scalar() or 0
    
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

@router.get("/sales-report")
async def get_sales_report(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monthly sales breakdown for the last few months"""
    current_year = datetime.now().year
    
    # Get sales by month (paid payments)
    monthly_sales = db.query(
        extract('month', models.Payment.created_at).label('month'),
        func.sum(models.Payment.amount).label('total')
    ).filter(
        models.Payment.status == 'paid',
        extract('year', models.Payment.created_at) == current_year
    ).group_by(
        extract('month', models.Payment.created_at)
    ).all()
    
    # Convert to dictionary for easy lookup
    sales_by_month = {int(row.month): float(row.total) for row in monthly_sales}
    
    # Get last 3 months dynamically
    current_month = datetime.now().month
    months_data = []
    
    for i in range(2, -1, -1):  # Get 3 months back including current
        month_num = current_month - i
        if month_num <= 0:
            month_num += 12
        
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        month_name = month_names[month_num - 1]
        amount = sales_by_month.get(month_num, 0)
        
        months_data.append({
            "month": month_name,
            "amount": amount
        })
    
    # Total sales (all time paid)
    total_sales = db.query(func.sum(models.Payment.amount)).filter(
        models.Payment.status == 'paid'
    ).scalar() or Decimal('0.00')
    
    return {
        "months": months_data,
        "total_sales": float(total_sales)
    }

@router.get("/rating-distribution")
async def get_rating_distribution(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get distribution of ratings (5, 4, 3, 2, 1 stars) for bar chart"""
    # Get count of reviews for each rating level
    total_reviews = db.query(func.count(models.Review.id)).scalar() or 0
    
    distribution = {}
    for rating in range(5, 0, -1):  # 5 to 1
        # Count reviews with this rating (rounded)
        count = db.query(func.count(models.Review.id)).filter(
            models.Review.rating >= rating - 0.5,
            models.Review.rating < rating + 0.5
        ).scalar() or 0
        
        percentage = (count / total_reviews * 100) if total_reviews > 0 else 0
        distribution[str(rating)] = {
            "count": count,
            "percentage": round(percentage, 1)
        }
    
    return {
        "distribution": distribution,
        "total_reviews": total_reviews
    }

@router.get("/top-items-chart")
async def get_top_items_with_sales(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 5
):
    """Get top selling items with their sales amounts for bar chart visualization"""
    # Get top items by total sales amount
    top_items = db.query(
        models.Item.name,
        func.sum(models.Payment.amount).label('total_sales'),
        func.count(models.Order.id).label('order_count')
    ).join(
        models.Order, models.Item.id == models.Order.item_id
    ).join(
        models.Payment, models.Order.id == models.Payment.order_id
    ).filter(
        models.Payment.status == 'paid',
        models.Item.is_deleted == 0
    ).group_by(
        models.Item.id, models.Item.name
    ).order_by(
        func.sum(models.Payment.amount).desc()
    ).limit(limit).all()
    
    return [
        {
            "name": item.name,
            "total_sales": float(item.total_sales),
            "order_count": item.order_count
        }
        for item in top_items
    ]
