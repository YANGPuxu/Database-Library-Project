from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, DECIMAL, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# 1. 管理员表
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(100)) # 存储明文或哈希

# 2. 读者表
class Reader(Base):
    __tablename__ = "readers"

    card_id = Column(Integer, primary_key=True, index=True) # 学号/借书证号
    name = Column(String(50))
    category = Column(String(20)) # 学生/教师/校外
    borrowed_count = Column(Integer, default=0) # 当前已借数量

# 3. 出版社表
class Publisher(Base):
    __tablename__ = "publishers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)
    address = Column(String(200))

# 4. 图书基本信息表
class Book(Base):
    __tablename__ = "books"

    isbn = Column(String(20), primary_key=True, index=True)
    title = Column(String(100))
    author = Column(String(100))
    publisher_id = Column(Integer, ForeignKey("publishers.id"))
    price = Column(DECIMAL(10, 2))
    stock_qty = Column(Integer, default=0) # 逻辑库存数量

# 5. 馆藏表 (具体的每一本书)
class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True) # 条码号
    isbn = Column(String(20), ForeignKey("books.isbn"))
    status = Column(Integer, default=1) 
    # 1=在馆, 0=已借出, -1=丢失/损毁

# 6. 借阅记录表 (这就是你报错缺失的那个！)
class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("readers.card_id"))
    inventory_id = Column(Integer, ForeignKey("inventory.id"))
    borrow_date = Column(DateTime, default=func.now()) # 借出时间
    return_date = Column(DateTime, nullable=True)      # 归还时间 (空表示未还)

# 7. 罚款记录表
class Fine(Base):
    __tablename__ = "fines"

    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("readers.card_id"))
    amount = Column(DECIMAL(10, 2)) # 罚款金额
    remark = Column(String(255))    # 罚款原因
    is_paid = Column(Integer, default=0) # 0=未缴, 1=已缴