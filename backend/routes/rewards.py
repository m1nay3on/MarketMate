"""
Reward routes for CRUD operations
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from backend.database.connection import get_db
from backend.models import models, schemas
from backend.utils.auth_utils import get_current_user

router = APIRouter(prefix="/api/rewards", tags=["Rewards"])

@router.get("/", response_model=List[schemas.RewardResponse])
async def get_all_rewards(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all rewards for current user"""
    rewards = db.query(models.Reward).filter(
        models.Reward.user_id == current_user.id
    ).all()
    
    # Update status based on validity_period
    for reward in rewards:
        if reward.validity_period < datetime.now() and reward.status == 'valid':
            reward.status = 'expired'
    db.commit()
    
    return rewards

@router.get("/{reward_id}", response_model=schemas.RewardResponse)
async def get_reward(
    reward_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific reward by ID"""
    reward = db.query(models.Reward).filter(
        models.Reward.id == reward_id,
        models.Reward.user_id == current_user.id
    ).first()
    
    if not reward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reward not found"
        )
    
    return reward

@router.post("/", response_model=schemas.RewardResponse, status_code=status.HTTP_201_CREATED)
async def create_reward(
    reward_data: schemas.RewardCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new reward"""
    # Check if reward_id already exists
    existing_id = db.query(models.Reward).filter(
        models.Reward.reward_id == reward_data.reward_id,
        models.Reward.user_id == current_user.id
    ).first()
    
    if existing_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reward ID already exists"
        )
    
    # Check if code already exists
    existing_code = db.query(models.Reward).filter(
        models.Reward.code == reward_data.code,
        models.Reward.user_id == current_user.id
    ).first()
    
    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reward code already exists"
        )
    
    new_reward = models.Reward(
        **reward_data.dict(),
        user_id=current_user.id,
        status='valid'
    )
    
    db.add(new_reward)
    db.commit()
    db.refresh(new_reward)
    
    return new_reward

@router.put("/{reward_id}", response_model=schemas.RewardResponse)
async def update_reward(
    reward_id: int,
    reward_data: schemas.RewardUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a reward"""
    reward = db.query(models.Reward).filter(
        models.Reward.id == reward_id,
        models.Reward.user_id == current_user.id
    ).first()
    
    if not reward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reward not found"
        )
    
    # Update only provided fields
    for field, value in reward_data.dict(exclude_unset=True).items():
        setattr(reward, field, value)
    
    db.commit()
    db.refresh(reward)
    
    return reward

@router.delete("/{reward_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reward(
    reward_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a reward"""
    reward = db.query(models.Reward).filter(
        models.Reward.id == reward_id,
        models.Reward.user_id == current_user.id
    ).first()
    
    if not reward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reward not found"
        )
    
    db.delete(reward)
    db.commit()
    
    return None

@router.get("/validate/{code}")
async def validate_reward_code(
    code: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Validate a reward code"""
    reward = db.query(models.Reward).filter(
        models.Reward.code == code,
        models.Reward.user_id == current_user.id
    ).first()
    
    if not reward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reward code not found"
        )
    
    # Check if expired
    is_valid = reward.validity_period >= datetime.now() and reward.status == 'valid'
    
    return {
        "valid": is_valid,
        "reward_id": reward.reward_id,
        "type": reward.type,
        "discount": float(reward.discount),
        "validity_period": reward.validity_period
    }
