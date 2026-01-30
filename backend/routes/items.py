"""
Item routes for CRUD operations
"""
import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.config import settings
from backend.models import models, schemas
from backend.utils.auth_utils import get_current_user

router = APIRouter(prefix="/api/items", tags=["Items"])

@router.get("/", response_model=List[schemas.ItemResponse])
async def get_all_items(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all items - regular users see active items only, admins see only their own for management"""
    if current_user.role == models.UserRole.admin:
        # Admin sees only their own non-deleted items for management
        items = db.query(models.Item).filter(
            models.Item.user_id == current_user.id,
            models.Item.is_deleted == 0
        ).all()
    else:
        # Regular users see ALL active items from all admins (marketplace view)
        # Filter out deleted items so they don't appear in user interface
        items = db.query(models.Item).filter(
            models.Item.is_deleted == 0
        ).all()
    return items

@router.get("/{item_id}", response_model=schemas.ItemResponse)
async def get_item(
    item_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific item by ID"""
    if current_user.role == models.UserRole.admin:
        # Admin can only get their own non-deleted items
        item = db.query(models.Item).filter(
            models.Item.id == item_id,
            models.Item.user_id == current_user.id,
            models.Item.is_deleted == 0
        ).first()
    else:
        # Regular users can view any non-deleted item
        item = db.query(models.Item).filter(
            models.Item.id == item_id,
            models.Item.is_deleted == 0
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
    """Soft delete an item - marks as deleted but preserves order history"""
    item = db.query(models.Item).filter(
        models.Item.id == item_id,
        models.Item.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Soft delete - set is_deleted flag instead of actually deleting
    # This preserves order history for this item
    item.is_deleted = 1
    db.commit()
    
    return None

@router.post("/{item_id}/upload-image")
async def upload_item_image(
    item_id: int,
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload an image for an item"""
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
    
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    # Save file
    try:
        contents = await file.read()
        if len(contents) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE // (1024*1024)}MB"
            )
        
        with open(file_path, "wb") as f:
            f.write(contents)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Update item with new image URL
    image_url = f"/{settings.UPLOAD_DIR}/{unique_filename}"
    item.image_url = image_url
    db.commit()
    db.refresh(item)
    
    return {"image_url": image_url, "message": "Image uploaded successfully"}

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
