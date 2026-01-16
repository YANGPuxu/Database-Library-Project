# 作用：设置数据库连接，创建 SQLAlchemy 引擎、会话和模型基类

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 数据库连接配置
# 格式: mysql+pymysql://用户名:密码@localhost:3306/数据库名
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:yangpuxu20050427@localhost:3306/library_sys"

# 创建引擎 (Engine)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

# 创建会话工厂 (SessionLocal)
# 以后我们在代码里操作数据库，都要通过这个 SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建模型基类 (Base)
# 后面所有的表模型都要继承这个 Base
Base = declarative_base()