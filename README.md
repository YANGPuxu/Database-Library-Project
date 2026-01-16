# 📚 图书馆管理系统 (Library Management System)

这是一个基于 **Vue 3** 和 **FastAPI** 前后端分离架构开发的图书馆管理系统。
本项目为数据库课程大作业，实现了读者管理、图书管理、借阅/归还流程以及罚款处理等核心功能。

## 🛠️ 技术栈 (Tech Stack)

* **前端 (Frontend)**: Vue 3, Vite, Element Plus, Axios
* **后端 (Backend)**: Python 3.8+, FastAPI, SQLAlchemy, PyMySQL
* **数据库 (Database)**: MySQL 8.0+

---

## 🚀 快速开始 (运行指南)

请确保本地已安装 **Python**, **Node.js** 以及 **MySQL**。

### 第一步：数据库配置

1. 在 MySQL 中创建一个名为 `library_sys` 的空数据库：

    ```sql
    CREATE DATABASE library_sys CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    ```

2. 根据您的实际情况选择以下一种方式初始化数据：
   1. 情况 A：从零开始 (全新部署) 直接执行后端的初始化脚本，系统会自动建表并写入演示数据：

        ```bash
        cd backend
        python init_db.py
        ```

   2. 情况 B：从备份文件恢复 (已有数据) 如果您本地有 「.sql」 备份文件，请通过 MySQL Workbench 导入.

3. 打开项目中的 `backend/database.py` 文件，修改数据库连接配置（用户名/密码）：

    ```python
    # 格式: mysql+pymysql://用户名:密码@localhost/数据库名
    SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:你的密码@localhost/library_sys"
    ```

### 第二步：后端启动 (Backend)

1. 进入后端目录：

    ```bash
    cd backend
    ```

2. 安装依赖（注意：python 版本需要为 3.10 及以上）：

    ```bash
    pip install -r requirements.txt
    ```

3. **初始化数据库与数据** (重要：此脚本会清空数据库并写入预设的管理员、书籍和借阅记录)：

    ```bash
    python init_db.py
    ```

    > 看到 `✅ [6/6] 数据库初始化完成！` 即表示成功。

4. 启动后端服务：

    ```bash
    uvicorn main:app --reload
    ```

    * API 文档地址: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 第三步：前端启动 (Frontend)

1. 打开一个新的终端窗口，进入前端目录：

    ```bash
    cd frontend
    ```

2. 安装依赖：

    ```bash
    npm install
    ```

3. 启动前端项目：

    ```bash
    npm run dev
    ```

4. 在浏览器访问：[http://localhost:5173](http://localhost:5173)

---

## 🔑 测试账号

数据库初始化脚本 (`init_db.py`) 会自动创建以下测试账号，您可以直接使用登录：

| 角色 | 用户名 | 密码 | 备注 |
| :--- | :--- | :--- | :--- |
| **管理员** | `admin1` | `123456` | 超级管理员权限 |
| **管理员** | `admin2` | `123456` | 备用账号 |

---

## 📂 目录结构说明

```text
LibraryProject/
├── backend/                # Python 后端代码
│   ├── main.py             # 核心路由与逻辑
│   ├── models.py           # 数据库模型 (ORM)
│   ├── schemas.py          # Pydantic 数据校验模型
│   ├── database.py         # 数据库连接配置
│   ├── init_db.py          # 数据库初始化/重置脚本
│   └── requirements.txt    # 后端依赖清单
│
├── frontend/               # Vue 前端代码
│   ├── src/
│   │   ├── views/          # 所有的页面文件 (Login, Home, BookManage...)
│   │   ├── utils/          # 工具类 (Axios封装)
│   │   └── style.css       # 全局样式
│   └── package.json        # 前端依赖清单
│
├── library_sys.sql         # (可选) 数据库结构备份
└── README.md               # 项目说明文档
```
