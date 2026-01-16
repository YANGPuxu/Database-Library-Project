from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# =======================
# 1. 基础模型 (作为父类)
# =======================
class UserLogin(BaseModel):
    username: str
    password: str

# =======================
# 2. 响应模型 (包含ID)
# =======================

# --- 读者 ---
class ReaderCreate(BaseModel):
    name: str
    category: str

class ReaderResponse(ReaderCreate):
    card_id: int
    borrowed_count: int
    unpaid_fine_count: int = 0  # 👈 新增这个字段 (默认值为0)
    
    class Config:
        from_attributes = True

# --- 出版社 ---
class PublisherCreate(BaseModel):
    name: str
    address: Optional[str] = None

class PublisherResponse(PublisherCreate):
    id: int
    class Config:
        from_attributes = True

# --- 图书基本信息 ---
class BookCreate(BaseModel):
    isbn: str
    title: str
    author: str
    publisher_id: int
    price: Optional[float] = 0.0

class BookResponse(BookCreate):
    stock_qty: int
    class Config:
        from_attributes = True

# --- 馆藏 (具体的一本书) ---
class InventoryCreate(BaseModel):
    isbn: str
    # 状态默认是 1 (在馆)

class InventoryResponse(InventoryCreate):
    id: int
    status: int
    class Config:
        from_attributes = True

# --- 借阅/归还 请求 ---
class BorrowRequest(BaseModel):
    card_id: int
    inventory_id: int

class ReturnRequest(BaseModel):
    inventory_id: int
    is_damaged: bool = False  # 默认没坏，前端可以传 true

# --- 借阅记录响应 ---
class BorrowRecordResponse(BaseModel):
    id: int
    card_id: int
    inventory_id: int
    borrow_date: datetime
    return_date: Optional[datetime]
    class Config:
        from_attributes = True

# --- 罚款记录 ---
class FineResponse(BaseModel):
    id: int
    card_id: int
    amount: float
    is_paid: int  # 0=未缴, 1=已缴
    remark: Optional[str] = None
    
    class Config:
        from_attributes = True