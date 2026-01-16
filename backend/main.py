from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from database import SessionLocal, engine
from sqlalchemy.exc import IntegrityError
import models, schemas
from fastapi.middleware.cors import CORSMiddleware

# 创建表 (确保表存在)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 允许所有来源 (比如 localhost:5173)
    allow_credentials=True,
    allow_methods=["*"],      # 允许所有方法 (GET, POST, PUT, DELETE...)
    allow_headers=["*"],      # 允许所有 Header
)

# 数据库依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===========================
# 1. 登录模块 
# ===========================
@app.post("/login/")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    # 简单的明文匹配，实际项目应加密
    db_user = db.query(models.User).filter(
        models.User.username == user.username, 
        models.User.password == user.password
    ).first()
    
    if not db_user:
        raise HTTPException(status_code=400, detail="用户名或密码错误") # [cite: 7]
    return {"message": "登录成功", "user_id": db_user.id} # [cite: 8]

# ===========================
# 2. 基础信息管理 (CRUD)
# ===========================

# --- 读者管理 [cite: 11-15] ---
@app.post("/readers/", response_model=schemas.ReaderResponse)
def create_reader(reader: schemas.ReaderCreate, db: Session = Depends(get_db)):
    db_reader = models.Reader(**reader.dict())
    db.add(db_reader)
    db.commit()
    db.refresh(db_reader)
    return db_reader

@app.get("/readers/", response_model=List[schemas.ReaderResponse])
def get_readers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
# 1. 查出所有读者
    readers = db.query(models.Reader).offset(skip).limit(limit).all()
    
    results = []
    for r in readers:
        # 2. 针对每个读者，去罚款表查一下：card_id是他 且 is_paid=0 (未缴) 的数量
        count = db.query(models.Fine).filter(
            models.Fine.card_id == r.card_id, 
            models.Fine.is_paid == 0
        ).count()
        
        # 3. 把这个数量塞进响应数据里
        # (因为 SQLAlchemy 对象默认不能直接赋值新属性，所以我们转成字典或者利用 setattr)
        # 这里用一种简单的方法：利用 Pydantic 的兼容性
        r.unpaid_fine_count = count 
        results.append(r)
        
    return results

@app.delete("/readers/{card_id}")
def delete_reader(card_id: int, db: Session = Depends(get_db)):
    # 1. 先查人是否存在
    db_reader = db.query(models.Reader).filter(models.Reader.card_id == card_id).first()
    if not db_reader:
        raise HTTPException(status_code=404, detail="读者不存在")
    
    # 2. 尝试删除，并捕获外键冲突
    try:
        db.delete(db_reader)
        db.commit()
    except IntegrityError:
        # 捕获到数据库的完整性错误（通常是外键依赖）
        db.rollback() # 💥 重要：事务失败后必须回滚，否则数据库连接会卡死
        raise HTTPException(
            status_code=400, 
            detail="无法删除：该读者仍有借阅记录或罚款记录未处理！"
        )
    return {"message": "删除成功"}

@app.put("/readers/{card_id}", response_model=schemas.ReaderResponse)
def update_reader(card_id: int, reader: schemas.ReaderCreate, db: Session = Depends(get_db)):
    db_reader = db.query(models.Reader).filter(models.Reader.card_id == card_id).first()
    if not db_reader:
        raise HTTPException(status_code=404, detail="读者不存在")
    
    db_reader.name = reader.name
    db_reader.category = reader.category
    db.commit()
    db.refresh(db_reader)
    return db_reader

# --- 出版社管理 [cite: 16] ---
@app.post("/publishers/", response_model=schemas.PublisherResponse)
def create_publisher(pub: schemas.PublisherCreate, db: Session = Depends(get_db)):
    # 1. 先去库里查一下，有没有同名的
    existing = db.query(models.Publisher).filter(models.Publisher.name == pub.name).first()
    if existing:
        # 如果有，直接报错，不往后执行了
        raise HTTPException(status_code=400, detail="该出版社名称已存在")

    db_pub = models.Publisher(**pub.dict())
    db.add(db_pub)
    db.commit()
    db.refresh(db_pub)
    return db_pub

@app.get("/publishers/", response_model=List[schemas.PublisherResponse])
def get_publishers(db: Session = Depends(get_db)):
    return db.query(models.Publisher).all()

from sqlalchemy.exc import IntegrityError # 👈 确保文件顶部已经导入了这个

@app.put("/publishers/{publisher_id}", response_model=schemas.PublisherResponse)
def update_publisher(publisher_id: int, pub: schemas.PublisherCreate, db: Session = Depends(get_db)):
    # 1. 查找目标出版社
    db_pub = db.query(models.Publisher).filter(models.Publisher.id == publisher_id).first()
    if not db_pub:
        raise HTTPException(status_code=404, detail="出版社不存在")
    
    # 2. 尝试更新数据
    try:
        db_pub.name = pub.name
        db_pub.address = pub.address
        db.commit() # 💥 这里是可能触发唯一性约束报错的地方
        db.refresh(db_pub)
        return db_pub
    except IntegrityError:
        # 3. 捕获冲突错误
        db.rollback() # ⚠️ 极其重要：操作失败后必须回滚，否则该数据库连接会失效
        raise HTTPException(
            status_code=400, 
            detail=f"修改失败：名称「{pub.name}」已被其他出版社占用，请更换名称。"
        )

@app.delete("/publishers/{publisher_id}")
def delete_publisher(publisher_id: int, db: Session = Depends(get_db)):
    db_pub = db.query(models.Publisher).filter(models.Publisher.id == publisher_id).first()
    if not db_pub:
        raise HTTPException(status_code=404, detail="出版社不存在")
    # 注意：如果该出版社下有书，删除可能会报错（外键约束）。
    # 为了作业简单，这里直接删。如果不让删，会抛出 500 错误，也算一种保护。
    try:
        db.delete(db_pub)
        db.commit()
    except Exception:
        raise HTTPException(status_code=400, detail="无法删除：该出版社下仍有图书")
    return {"message": "删除成功"}

# --- 图书基本信息管理 [cite: 18] ---
@app.post("/books/", response_model=schemas.BookResponse)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    # 0. 检查 ISBN 唯一性
    if db.query(models.Book).filter(models.Book.isbn == book.isbn).first():
        raise HTTPException(status_code=400, detail="ISBN 号不可相同")

    # 1. 检查出版社是否存在
    if not db.query(models.Publisher).filter(models.Publisher.id == book.publisher_id).first():
         raise HTTPException(status_code=404, detail="出版社不存在")
    
    # 2. 🛡️ 检查价格是否超标 (防止数据库报错)
    # DECIMAL(10, 2) 最大整数位是 8 位
    if book.price and book.price > 99999999:
        raise HTTPException(status_code=400, detail="价格数值过大 (最大允许 99999999)")

    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.get("/books/", response_model=List[schemas.BookResponse])
def get_books(db: Session = Depends(get_db)):
    return db.query(models.Book).all()

# 修改/删除图书
@app.put("/books/{isbn}", response_model=schemas.BookResponse)
def update_book(isbn: str, book: schemas.BookCreate, db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.isbn == isbn).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="图书不存在")
    
    # 👇 新增：价格检查逻辑
    if book.price and book.price > 99999999:
        raise HTTPException(status_code=400, detail="价格数值过大 (最大允许 99999999)")

    # 👇 新增：同上，既然允许改出版社，也要检查这个新出版社存不存在
    if not db.query(models.Publisher).filter(models.Publisher.id == book.publisher_id).first():
         raise HTTPException(status_code=404, detail="出版社不存在")
    
    db_book.title = book.title
    db_book.author = book.author
    db_book.publisher_id = book.publisher_id
    db_book.price = book.price
    db.commit()
    db.refresh(db_book)
    return db_book

@app.delete("/books/{isbn}")
def delete_book(isbn: str, db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.isbn == isbn).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="图书不存在")
    try:
        db.delete(db_book)
        db.commit()
    except Exception:
        raise HTTPException(status_code=400, detail="无法删除：该书可能有馆藏或借阅记录")
    return {"message": "删除成功"}

# --- 馆藏管理 [cite: 20] ---
@app.post("/inventory/", response_model=schemas.InventoryResponse)
def create_inventory(item: schemas.InventoryCreate, db: Session = Depends(get_db)):
    # 1. 检查ISBN是否存在
    db_book = db.query(models.Book).filter(models.Book.isbn == item.isbn).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="图书ISBN不存在")
    
    # 2. 添加馆藏
    db_item = models.Inventory(**item.dict())
    db.add(db_item)
    
    # 3. 联动: 图书总库存 +1 (可选，方便查询)
    db_book.stock_qty += 1
    
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/inventory/", response_model=List[schemas.InventoryResponse])
def get_inventory(db: Session = Depends(get_db)):
    return db.query(models.Inventory).all()

@app.put("/inventory/{id}", response_model=schemas.InventoryResponse)
def update_inventory(id: int, item: schemas.InventoryCreate, db: Session = Depends(get_db)):
    db_item = db.query(models.Inventory).filter(models.Inventory.id == id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="馆藏不存在")
    
    # 这里一般只修改 ISBN (比如录入错了)，状态通常由借还书接口管理
    db_item.isbn = item.isbn
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/inventory/{id}")
def delete_inventory(id: int, db: Session = Depends(get_db)):
    db_item = db.query(models.Inventory).filter(models.Inventory.id == id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="馆藏不存在")
    
    # 如果书借出去了(status=0)，不允许删除
    if db_item.status == 0:
         raise HTTPException(status_code=400, detail="该书已借出，无法删除")
         
    # 删除同时要记得把书的库存 -1
    db_book = db.query(models.Book).filter(models.Book.isbn == db_item.isbn).first()
    if db_book and db_book.stock_qty > 0:
        db_book.stock_qty -= 1
        
    db.delete(db_item)
    db.commit()
    return {"message": "删除成功"}

# ===========================
# 3. 核心业务: 借阅与归还 (难点)
# ===========================

# --- 借书 [cite: 22-25] ---
@app.post("/borrow/")
def borrow_book(req: schemas.BorrowRequest, db: Session = Depends(get_db)):
    # 1. 检查读者
    reader = db.query(models.Reader).filter(models.Reader.card_id == req.card_id).first()
    if not reader:
        raise HTTPException(status_code=404, detail="读者不存在")

    # 如果读者有未缴罚款，不允许借阅
    unpaid_count = db.query(models.Fine).filter(
        models.Fine.card_id == req.card_id,
        models.Fine.is_paid == 0
    ).count()
    if unpaid_count > 0:
        raise HTTPException(status_code=400, detail="该读者有未缴罚款，无法借阅")
        
    # 2. 检查书籍状态 (必须在馆 status=1)
    item = db.query(models.Inventory).filter(models.Inventory.id == req.inventory_id).first()
    if not item or item.status != 1:
        raise HTTPException(status_code=400, detail="该书已被借出或不存在")

    # 3. 开启事务，执行一系列更新
    try:
        # A. 创建借阅记录 [cite: 24]
        record = models.BorrowRecord(card_id=req.card_id, inventory_id=req.inventory_id)
        db.add(record)
        
        # B. 更新馆藏状态 -> 借出(0) [cite: 24]
        item.status = 0
        
        # C. 更新读者已借数量 [cite: 25]
        reader.borrowed_count += 1
        
        # D. 更新图书基本信息(库存 -1) [cite: 24]
        book = db.query(models.Book).filter(models.Book.isbn == item.isbn).first()
        book.stock_qty -= 1
        
        db.commit()
        return {"message": "借阅成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# --- 还书 [cite: 26-30] ---
@app.post("/return/")
def return_book(req: schemas.ReturnRequest, db: Session = Depends(get_db)):
    # 1. 找到该书当前未归还的借阅记录
    record = db.query(models.BorrowRecord).filter(
        models.BorrowRecord.inventory_id == req.inventory_id,
        models.BorrowRecord.return_date == None
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="未找到该书的在借记录")

    try:
        # 2. 准备数据对象
        # A. 借阅记录
        record.return_date = datetime.now()
        
        # B. 馆藏信息
        item = db.query(models.Inventory).filter(models.Inventory.id == req.inventory_id).first()
        # 如果损坏，状态可以设为 2 (假设 2 代表损坏/维修中)，或者为了测试方便还是设为 1 (在馆)
        # 这里为了作业流程顺畅，我们设为 1，但备注里会写损坏
        item.status = 1 
        
        # C. 读者信息
        reader = db.query(models.Reader).filter(models.Reader.card_id == record.card_id).first()
        reader.borrowed_count -= 1
        
        # D. 图书基本信息 (获取价格用于赔偿)
        book = db.query(models.Book).filter(models.Book.isbn == item.isbn).first()
        book.stock_qty += 1
        
        # ===========================
        # E. 核心逻辑: 罚款计算
        # ===========================
        total_fine = 0.0
        remark_list = []

        # 1. 计算超期费
        # 假设借阅期限是 30 天
        days_borrowed = (record.return_date - record.borrow_date).days
        overdue_days = days_borrowed - 30
        if overdue_days > 0:
            overdue_fine = overdue_days * 0.5 # 每天 5 毛
            total_fine += overdue_fine
            remark_list.append(f"超期{overdue_days}天(￥{overdue_fine})")
        
        # 2. 计算损坏赔偿
        if req.is_damaged:
            # 如果书没有录入价格，默认赔 50 块 (防止报错)
            damage_fine = float(book.price) if book.price else 50.0
            total_fine += damage_fine
            remark_list.append(f"图书损坏赔偿(￥{damage_fine})")

        # 3. 如果有罚款，生成记录
        msg = "归还成功"
        if total_fine > 0:
            final_remark = "，".join(remark_list)
            fine = models.Fine(
                card_id=reader.card_id, 
                amount=total_fine, 
                remark=final_remark
            )
            db.add(fine)
            msg = f"归还成功，产生罚款：{final_remark}，总计 {total_fine} 元"

        db.commit()
        return {"message": msg}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# --- 获取某人的借阅记录 ---
@app.get("/borrow_records/{card_id}")
def get_borrow_records(card_id: int, db: Session = Depends(get_db)):
    return db.query(models.BorrowRecord).filter(models.BorrowRecord.card_id == card_id).all()

# 新增接口：获取所有罚款记录 (用于管理员总览)
@app.get("/fines/all", response_model=List[schemas.FineResponse])
def read_all_fines(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    # 按时间倒序，最新的罚款在最前面
    fines = db.query(models.Fine).order_by(models.Fine.id.desc()).offset(skip).limit(limit).all()
    return fines

@app.get("/fines/{card_id}", response_model=List[schemas.FineResponse])
def get_fines(card_id: int, db: Session = Depends(get_db)):
    return db.query(models.Fine).filter(models.Fine.card_id == card_id).all()

#  缴纳罚款
@app.post("/fines/pay/{fine_id}")
def pay_fine(fine_id: int, db: Session = Depends(get_db)):
    fine = db.query(models.Fine).filter(models.Fine.id == fine_id).first()
    if not fine:
        raise HTTPException(status_code=404, detail="罚款单不存在")
    
    if fine.is_paid == 1:
        return {"message": "该罚款已缴纳，无需重复缴费"}
    
    fine.is_paid = 1
    db.commit()
    return {"message": "缴费成功"}