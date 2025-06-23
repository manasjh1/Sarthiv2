import uuid
import enum
from sqlalchemy import (
    Column, String, Integer, BigInteger, ForeignKey, DateTime, Text, Boolean, Enum, SmallInteger
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

# === Enum Definitions (Match your database) ===

class UserTypeEnum(str, enum.Enum):
    user = "user"
    admin = "admin"

class ReflectionModeEnum(str, enum.Enum):
    guided = "guided"
    collaborative = "collaborative"

class DeliveryModeEnum(str, enum.Enum):
    whatsapp = "whatsapp"
    email = "email"
    private = "private"

# === Table: users ===
class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(256), nullable=False)
    email = Column(String(256), nullable=False, unique=True)
    phone_number = Column(BigInteger)  # ✅ Changed to BigInteger to match BIGINT
    user_type = Column(
        Enum(UserTypeEnum, name="user_type_enum", create_type=False),
        default=UserTypeEnum.user
    )
    proficiency_score = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(SmallInteger, default=1)  # ✅ Changed to SmallInteger
    
    # Relationships
    given_reflections = relationship("Reflection", back_populates="giver", foreign_keys="[Reflection.giver_user_id]")
    received_reflections = relationship("Reflection", back_populates="receiver", foreign_keys="[Reflection.receiver_user_id]")

# === Table: stages_dict ===
class StageDict(Base):
    __tablename__ = "stages_dict"

    stage_no = Column(Integer, primary_key=True)
    stage_name = Column(String(256), nullable=False, unique=True)
    status = Column(SmallInteger, default=1)
    
    # Relationships
    reflections = relationship("Reflection", back_populates="stage")
    messages = relationship("Message", back_populates="stage")

# === Table: category_dict ===
class CategoryDict(Base):
    __tablename__ = "category_dict"

    category_no = Column(Integer, primary_key=True)
    category_name = Column(String(256), nullable=False, unique=True)
    status = Column(SmallInteger, default=1)
    
    # Relationships
    reflections = relationship("Reflection", back_populates="category")

# === Table: reflections ===
class Reflection(Base):
    __tablename__ = "reflections"

    reflection_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    stage_no = Column(Integer, ForeignKey("stages_dict.stage_no"), nullable=False)
    category_no = Column(Integer, ForeignKey("category_dict.category_no"), nullable=False)
    receiver_user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    giver_user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    mode = Column(
        Enum(ReflectionModeEnum, name="reflection_mode", create_type=False),
        default=ReflectionModeEnum.guided
    )
    name = Column(String(256))
    relation = Column(String(256))
    status = Column(SmallInteger, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    reflection = Column(Text)
    delivery_mode = Column(
        Enum(DeliveryModeEnum, name="reflection_delivery_mode", create_type=False),
        default=DeliveryModeEnum.email
    )
    
    # Relationships
    giver = relationship("User", back_populates="given_reflections", foreign_keys=[giver_user_id])
    receiver = relationship("User", back_populates="received_reflections", foreign_keys=[receiver_user_id])
    stage = relationship("StageDict", back_populates="reflections")
    category = relationship("CategoryDict", back_populates="reflections")
    messages = relationship("Message", back_populates="reflection")

# === Table: messages ===
class Message(Base):
    __tablename__ = "messages"

    message_id = Column(BigInteger, primary_key=True, autoincrement=True)  # ✅ BIGSERIAL
    text = Column(Text, nullable=False)
    reflection_id = Column(UUID(as_uuid=True), ForeignKey("reflections.reflection_id"), nullable=False)
    sender = Column(SmallInteger, nullable=False)
    status = Column(SmallInteger, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_distress = Column(Boolean, default=False)
    stage_no = Column(Integer, ForeignKey("stages_dict.stage_no"), nullable=False)
    
    # Relationships
    reflection = relationship("Reflection", back_populates="messages")
    stage = relationship("StageDict", back_populates="messages")