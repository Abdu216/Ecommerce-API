from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List
from datetime import datetime, timedelta
from app.api import deps
from app.schemas.sale import RevenueAnalytics, CategoryRevenue, RevenuePeriodComparison
from app.models import (
    User, Sale as SaleModel,
    Category as CategoryModel,
    Product as ProductModel
)

router = APIRouter()


def get_revenue_data(
    db: Session,
    start_date: datetime,
    end_date: datetime,
    period: str
) -> RevenueAnalytics:
    """Helper function to calculate revenue analytics for a given period."""
    query = db.query(
        func.sum(SaleModel.total_amount).label("total_revenue"),
        func.count(SaleModel.id).label("total_sales")
    ).filter(
        SaleModel.sale_date >= start_date,
        SaleModel.sale_date <= end_date
    )
    
    result = query.first()
    total_revenue = float(result.total_revenue or 0)
    total_sales = int(result.total_sales or 0)
    avg_order_value = total_revenue / total_sales if total_sales > 0 else 0
    
    return RevenueAnalytics(
        period=period,
        start_date=start_date,
        end_date=end_date,
        total_revenue=total_revenue,
        total_sales=total_sales,
        average_order_value=avg_order_value
    )


@router.get("/revenue", response_model=RevenueAnalytics)
def get_revenue(
    period: str = Query(..., enum=["daily", "weekly", "monthly", "annual"]),
    date: datetime = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_staff)
):
    """Get revenue analytics for a specific period (staff only)."""
    if date is None:
        date = datetime.now()
    
    if period == "daily":
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
    elif period == "weekly":
        start_date = date - timedelta(days=date.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=7)
    elif period == "monthly":
        start_date = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if date.month == 12:
            end_date = date.replace(year=date.year + 1, month=1, day=1)
        else:
            end_date = date.replace(month=date.month + 1, day=1)
    else:  # annual
        start_date = date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = date.replace(year=date.year + 1, month=1, day=1)
    
    return get_revenue_data(db, start_date, end_date, period)


@router.get("/revenue/comparison", response_model=RevenuePeriodComparison)
def compare_revenue(
    period: str = Query(..., enum=["daily", "weekly", "monthly", "annual"]),
    date1: datetime = None,
    date2: datetime = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_staff)
):
    """Compare revenue between two periods (staff only)."""
    if date1 is None:
        date1 = datetime.now()
    if date2 is None:
        if period == "daily":
            date2 = date1 - timedelta(days=1)
        elif period == "weekly":
            date2 = date1 - timedelta(weeks=1)
        elif period == "monthly":
            if date1.month == 1:
                date2 = date1.replace(year=date1.year - 1, month=12)
            else:
                date2 = date1.replace(month=date1.month - 1)
        else:  # annual
            date2 = date1.replace(year=date1.year - 1)
    
    period1 = get_revenue_data(db, date1, date1, period)
    period2 = get_revenue_data(db, date2, date2, period)
    
    revenue_change = ((period1.total_revenue - period2.total_revenue) / period2.total_revenue * 100
                     if period2.total_revenue > 0 else 0)
    sales_change = ((period1.total_sales - period2.total_sales) / period2.total_sales * 100
                   if period2.total_sales > 0 else 0)
    
    return RevenuePeriodComparison(
        period_1=period1,
        period_2=period2,
        revenue_change_percentage=revenue_change,
        sales_change_percentage=sales_change
    )


@router.get("/revenue/categories", response_model=List[CategoryRevenue])
def get_category_revenue(
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_staff)
):
    """Get revenue breakdown by category (staff only)."""
    if start_date is None:
        start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if end_date is None:
        end_date = datetime.now()
    
    # Get total revenue for the period
    total_revenue_result = db.query(
        func.sum(SaleModel.total_amount).label("total")
    ).filter(
        SaleModel.sale_date >= start_date,
        SaleModel.sale_date <= end_date
    ).scalar()
    
    total_revenue = float(total_revenue_result or 0)
    
    # Get revenue by category
    category_revenues = db.query(
        CategoryModel.id,
        CategoryModel.name,
        func.sum(SaleModel.total_amount).label("revenue"),
        func.count(SaleModel.id).label("sales")
    ).join(
        ProductModel, ProductModel.category_id == CategoryModel.id
    ).join(
        SaleModel, SaleModel.product_id == ProductModel.id
    ).filter(
        SaleModel.sale_date >= start_date,
        SaleModel.sale_date <= end_date
    ).group_by(
        CategoryModel.id,
        CategoryModel.name
    ).all()
    
    return [
        CategoryRevenue(
            category_id=cat.id,
            category_name=cat.name,
            total_revenue=float(cat.revenue or 0),
            total_sales=int(cat.sales or 0),
            percentage_of_total=(float(cat.revenue or 0) / total_revenue * 100 if total_revenue > 0 else 0)
        )
        for cat in category_revenues
    ] 