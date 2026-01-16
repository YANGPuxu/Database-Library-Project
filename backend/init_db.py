import models
from database import engine, SessionLocal
from datetime import datetime, timedelta

# ❌ 删除了 passlib 相关的引用，不再进行加密

def init_db():
    db = SessionLocal()
    
    print("🔥 [1/6] 正在清空旧数据库...")
    models.Base.metadata.drop_all(bind=engine)
    
    print("🏗️ [2/6] 正在重建表结构...")
    models.Base.metadata.create_all(bind=engine)
    
    print("👮 [3/6] 正在创建管理员账号 (明文密码)...")
    
    # ✅ 修改点：直接存储明文字符串 "123456"
    admins = [
        models.User(username="admin1", password="123456"),
        models.User(username="admin2", password="123456"),
        models.User(username="admin3", password="123456"),
    ]
    db.add_all(admins)
    db.commit()

    print("📚 [4/6] 正在录入基础数据 (出版社/图书/读者)...")
    
    # --- 1. 出版社 ---
    pubs = [
        models.Publisher(name="清华大学出版社", address="北京海淀区"),    # ID: 1
        models.Publisher(name="机械工业出版社", address="北京西城区"),    # ID: 2
        models.Publisher(name="人民文学出版社", address="北京朝阳区"),    # ID: 3
        models.Publisher(name="O'Reilly Media", address="California"),   # ID: 4
    ]
    db.add_all(pubs)
    db.commit()

    # --- 2. 图书 ---
    books = [
        models.Book(isbn="978-7-302", title="深入理解计算机系统", author="Randal E.Bryant", publisher_id=1, price=139.00, stock_qty=3),
        models.Book(isbn="978-7-111", title="算法导论", author="Thomas H.Cormen", publisher_id=2, price=128.00, stock_qty=2),
        models.Book(isbn="978-7-020", title="百年孤独", author="马尔克斯", publisher_id=3, price=55.00, stock_qty=1),
        models.Book(isbn="978-0-596", title="Learning Python", author="Mark Lutz", publisher_id=4, price=350.00, stock_qty=2),
    ]
    db.add_all(books)
    db.commit()

    # --- 3. 读者 ---
    readers = [
        models.Reader(name="李华", category="学生"),    # ID: 1
        models.Reader(name="韩梅梅", category="学生"),  # ID: 2
        models.Reader(name="罗辑", category="教师"),    # ID: 3
        models.Reader(name="章北海", category="校外人员"), # ID: 4
    ]
    db.add_all(readers)
    db.commit()

    print("📦 [5/6] 正在录入库存与借阅记录...")

    # --- 4. 库存 (Inventory) ---
    inv1 = models.Inventory(isbn="978-7-302", status=1) # 在馆
    inv2 = models.Inventory(isbn="978-7-302", status=0) # 已借出 (李华)
    inv3 = models.Inventory(isbn="978-7-302", status=1) # 在馆
    
    inv4 = models.Inventory(isbn="978-7-111", status=0) # 已借出 (韩梅梅)
    inv5 = models.Inventory(isbn="978-7-111", status=1) # 在馆

    inv6 = models.Inventory(isbn="978-7-020", status=1) # 在馆

    inv7 = models.Inventory(isbn="978-0-596", status=1) # 在馆
    inv8 = models.Inventory(isbn="978-0-596", status=1) # 在馆

    db.add_all([inv1, inv2, inv3, inv4, inv5, inv6, inv7, inv8])
    db.commit()

    # --- 5. 借阅记录 (BorrowRecord) ---
    # 李华借书
    b1 = models.BorrowRecord(
        card_id=1, 
        inventory_id=2, 
        borrow_date=datetime.now() - timedelta(days=5),
        return_date=None 
    )
    # 更新李华已借数量
    db.query(models.Reader).filter(models.Reader.card_id == 1).first().borrowed_count = 1

    # 韩梅梅借书
    b2 = models.BorrowRecord(
        card_id=2, 
        inventory_id=4, 
        borrow_date=datetime.now() - timedelta(days=10),
        return_date=None 
    )
    # 更新韩梅梅已借数量
    db.query(models.Reader).filter(models.Reader.card_id == 2).first().borrowed_count = 1

    db.add_all([b1, b2])
    db.commit()

    print("✅ [6/6] 数据库初始化完成！")
    print("   管理员账号: admin1 / 123456 (明文)")
    
    db.close()

if __name__ == "__main__":
    init_db()