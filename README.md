# FastAPI Project Demo

###### 声明：此仓库仅做为 FastAPI 入门级参考, 开箱即用, 所有接口采用 restful 风格

我的其他类似项目：

- fastapi 项目基础架构模板 [fastapi_best_architecture](https://github.com/wu-clan/fastapi_best_architecture)  
- fastapi tortoise-orm demo [fastapi_tortoise_mysql](https://github.com/wu-clan/fastapi_tortoise_mysql)

## 分支说明

所有分支均已停止维护，仅供参考

### 异步：

#### async -> master

```text
fastapi-0.85.1 + sqlalchemy2.0 + alembic + asyncmy + aioredis

✨: 邮箱验证码登录
```

#### async -> async-CRUDBase

```text
fastapi + sqlalchemy2.0 + alembic + asyncmy + aioredis + APScheduler

✨: 在 master 分支基础上扩展，集成 CRUD 封装和 APScheduler 定时任务
```

#### async -> async-Plus

```text
fastapi-0.95.0 + sqlalchemy2.0 + alembic + asyncmy + aioredis + APScheduler + PyCasbin

✨: 在 async-CRUDBase 分支基础上扩展，集成来自 PyCasbin 的 RBAC 鉴权
```

### 同步：

#### sync -> sync

```text
fastapi-0.85.1 + sqlalchemy2.0 + alembic + pymysql + redis

✨: 图片验证码登录
```

#### sync -> sync-CRUDBase

```text
fastapi + sqlalchemy2.0 + alembic + pymysql + redis + APScheduler

✨: 在 sync 分支基础上扩展，集成 CRUD 封装和 APScheduler 定时任务
```

#### sync -> sync-Plus

```text
fastapi-0.95.0 + sqlalchemy2.0 + alembic + pymysql + redis + APScheduler + PyCasbin

✨: 在 sync-CRUDBase 分支基础上扩展，集成来自 PyCasbin 的 RBAC 鉴权
```

## 下载：

### 1. 克隆仓库

全部分支:

```shell
git clone https://gitee.com/wu_cl/fastapi_sqlalchemy_mysql.git
```

指定分支:

```shell
git clone -b 分支名 https://gitee.com/wu_cl/fastapi_sqlalchemy_mysql.git
```

### 2. 使用 CLI（推荐）

pip 安装:

```shell
pip install fastapi-ccli
```

跳转查看使用说明:

- [PyPI](https://pypi.org/project/fastapi-ccli)
- [Gitee](https://gitee.com/wu_cl/fastapi_ccli)
- [GitHub](https://github.com/wu-clan/fastapi_ccli)

## 安装使用:

> ⚠️: 此过程请格外注意端口占用情况, 特别是 8000, 3306, 6379...

### 1：传统

1. 安装依赖
    ```shell
    pip install -r requirements.txt
    ```

2. 创建数据库 fsm, 选择 utf8mb4 编码
3. 查看 backend/app/core/conf.py 配置文件, 检查并修改数据库配置信息
4. 执行数据库迁移 [alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
    ```shell
    cd backend/app/
    
    # 生成迁移文件
    alembic revision --autogenerate
    
    # 执行迁移
    alembic upgrade head
    ```

5. 安装启动 redis
6. 查看 backend/app/core/conf.py 配置文件, 检查并修改 redis 配置信息
7. 执行 backend/app/main.py 文件启动服务
8. 浏览器访问: http://127.0.0.1:8000/v1/docs

---

### 2：docker

1. 在 docker-compose.yml 文件所在目录下执行一键启动命令

    ```shell
    docker-compose up -d --build
    ```
2. 等待命令自动执行完成

3. 浏览器访问: http://127.0.0.1:8000/v1/docs

## 初始化测试数据

执行 backend/app/init_test_data.py 文件

## 目录结构

结构树基本大致相同，详情请查看源代码

```text
├── backend
│   └── app
│       ├── alembic
│       ├── api
│       │   └── v1
│       ├── common
│       ├── core
│       ├── crud
│       ├── database
│       ├── middleware
│       ├── models
│       ├── schemas
|       |—— static
│       ├── test
│       └── utils
├── LICENSE
├── README.md
└── requirements.txt
```
