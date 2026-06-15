# schema.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SigninSchema(BaseModel):
    username: str
    password: str

class SignupSchema(BaseModel):
    fullname: str
    email: str
    password: str
    phone: str

class UserUpdateSchema(BaseModel):
    fullname: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[int] = None

class ResourceCreateSchema(BaseModel):
    resource_name: str
    resource_type: str
    description: Optional[str] = None
    total_quantity: int
    available_quantity: int

class ResourceUpdateSchema(BaseModel):
    resource_name: Optional[str] = None
    resource_type: Optional[str] = None
    description: Optional[str] = None
    total_quantity: Optional[int] = None
    available_quantity: Optional[int] = None

class BookingCreateSchema(BaseModel):
    resource_id: int
    quantity: int
    start_time: datetime
    end_time: datetime
    purpose: Optional[str] = None