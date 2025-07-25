from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reward_amount = Column(DECIMAL(10, 2), nullable=True)  # 奖励金额，支持小数
    status = Column(String(50), nullable=False, default="open")  # open, in_progress, completed, cancelled
    skill_tags = Column(ARRAY(String), nullable=True)  # 技能标签，存储为字符串数组
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    creator = relationship("User", back_populates="tasks")