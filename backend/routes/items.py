"""
Item routes for CRUD operations
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models import models, schemas
from backend.utils.auth_utils import get_current_user

router = APIRouter(prefix="/api/items", tags=["Items"])

@router.get("/", response_model=List[schemas.ItemResponse])
async def get_all_items(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all items for current user"""
    items = db.query(models.Item).filter(
        models.Item.user_id == current_user.id
    ).all()
    return items

@router.get("/{item_id}", response_model=schemas.ItemResponse)
async def get_item(
    item_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific item by ID"""
    item = db.query(models.Item).filter(
        models.Item.id == item_id,
        models.Item.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    return item

@router.post("/", response_model=schemas.ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: schemas.ItemCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new item"""
    # Check if item_id already exists globally (UNIQUE constraint in DB)
    existing = db.query(models.Item).filter(
        models.Item.item_id == item_data.item_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item ID already exists. Please use a different Item ID."
        )
    
    # Extract variants before creating item
    variants_list = item_data.variants
    item_dict = item_data.dict()
    del item_dict['variants']
    
    new_item = models.Item(
        **item_dict,
        user_id=current_user.id
    )
    
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    # Add variants if provided
    if variants_list:
        for variant_name in variants_list:
            variant = models.ItemVariant(
                item_id=new_item.id,
                variant_name=variant_name
            )
            db.add(variant)
        db.commit()
        db.refresh(new_item)
    
    return new_item

@router.put("/{item_id}", response_model=schemas.ItemResponse)
async def update_item(
    item_id: int,
    item_data: schemas.ItemUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an item"""
    item = db.query(models.Item).filter(
        models.Item.id == item_id,
        models.Item.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Update only provided fields
    for field, value in item_data.dict(exclude_unset=True).items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    
    return item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an item"""
    item = db.query(models.Item).filter(
        models.Item.id == item_id,
        models.Item.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    db.delete(item)
    db.commit()
    
    return None

@router.get("/{item_id}/variants")
async def get_item_variants(
    item_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all variants for an item"""
    item = db.query(models.Item).filter(
        models.Item.id == item_id,
        models.Item.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    variants = db.query(models.ItemVariant).filter(
        models.ItemVariant.item_id == item_id
    ).all()
    
    return [{"id": v.id, "variant_name": v.variant_name} for v in variants]
