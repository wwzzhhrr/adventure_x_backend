from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas import UserCreate, UserLogin, Token, UserResponse, UserUpdateBio
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user_from_token
from datetime import timedelta
from typing import Optional
from app.schemas import UserProfileResponse
from app.services.blockchain import CommuCoinService

router = APIRouter()


@router.post("/register", response_model=Token)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查邮箱是否已存在
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 检查用户名是否已存在
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        password=hashed_password,
        bio=user.bio
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # 自动生成钱包
    from app.services.blockchain import CommuCoinService
    blockchain = CommuCoinService()
    wallet = await blockchain.create_wallet()
    db_user.wallet_address = wallet["address"]
    db_user.wallet_public_key = wallet["public_key"]
    db_user.wallet_private_key = wallet["encrypted_private_key"]
    db.commit()
    db.refresh(db_user)
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(db_user)
    }


@router.get("/me", response_model=UserProfileResponse)
async def get_user_profile(
    current_user_email: str = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """获取当前用户的所有信息，用于‘我的’页面"""
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    service = CommuCoinService()
    balance = await service.get_comu_balance(user.wallet_address)
    
    return UserProfileResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        bio=user.bio,
        created_at=user.created_at,
        updated_at=user.updated_at,
        wallet_address=user.wallet_address,
        balance=balance
    )


@router.put("/update-bio", response_model=UserResponse)
def update_user_bio(
    bio_data: UserUpdateBio,
    db: Session = Depends(get_db),
    user_email: str = Depends(get_current_user_from_token)
):
    """更新用户bio"""
    # 查找用户
    db_user = db.query(User).filter(User.email == user_email).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 更新bio
    db_user.bio = bio_data.bio
    db.commit()
    db.refresh(db_user)
    
    return UserResponse.model_validate(db_user)


@router.post("/login", response_model=Token)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    # 查找用户（通过邮箱）
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(db_user)
    }
