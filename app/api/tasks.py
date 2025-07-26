from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal

from app.database import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas import TaskCreate, TaskResponse
from app.auth import get_current_user_from_token
from app.services.blockchain import CommuCoinService

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user_email: str = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    创建新任务
    """
    # 获取当前用户
    current_user = db.query(User).filter(User.email == current_user_email).first()
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 创建任务
    # Check blockchain balance
    service = CommuCoinService()
    balance = await service.get_balance(current_user.wallet_address)
    if balance < Decimal(task_data.reward_amount):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance to create task"
        )
    
    db_task = Task(
        title=task_data.title,
        description=task_data.description,
        creator_id=current_user.id,
        reward_amount=task_data.reward_amount,
        skill_tags=task_data.skill_tags,
        status="open"  # 默认状态为开放
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return db_task

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    current_user_email: str = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    获取任务列表（排除当前用户创建的任务）
    """
    # 获取当前用户
    current_user = db.query(User).filter(User.email == current_user_email).first()
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 查询所有任务，但排除当前用户创建的任务
    tasks = db.query(Task).filter(Task.creator_id != current_user.id).offset(skip).limit(limit).all()
    return tasks

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """
    获取单个任务详情
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    return task

@router.get("/my/created", response_model=List[TaskResponse])
async def get_my_created_tasks(
    current_user_email: str = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    获取当前用户创建的任务
    """
    # 获取当前用户
    current_user = db.query(User).filter(User.email == current_user_email).first()
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    tasks = db.query(Task).filter(Task.creator_id == current_user.id).all()
    return tasks