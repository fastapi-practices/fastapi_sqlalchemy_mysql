# FastAPI Project Demo

###### 声明：此仓库仅做为 FastAPI 入门级参考, 开箱即用, 所有接口采用 restful 风格

---

📢 2022 年 10 月 29 日, 更新提醒:

- 我想覆盖以前所有的提交, 这是一个让我难以决定的事实, 因为在所有功能的提交说明中, 有很多让
  人们误解的东西, 对于关注提交信息的人来讲, 存在很多误导性, 并且我是一个高度强迫症患者, 我没有
  理由拒绝此次决定
- 将升级一些核心库: fastapi, pydantic, sqlalchemy... 为了保持兼容性, 你可能必须同步
  仓库状态来保持他们的全局可用性
- 对以前复刻,点星和下载的人们说声抱歉, 如果你直接使用它作为了基础开发环境, 那可能会对你造成
  不必要的困扰, 我也不建议将它直接作为你的基础开发环境, 但是作为入门参考, 它应该会给你一些启发,
  并且这也是此仓库的主要目的

🏁 我将在后面的空闲时间对现有维护分支进行逐一更新, 这可能是一个漫长的过程, 在分支完成更新前,
它的原有分支提交不会被覆盖, 仍然可以从中获取部分参考, 但作为旧的内容, 我个人不提倡; 在所有现有
维护分支更新完毕后, 考虑将它们以发版的形式作为初始标记, 预计年前完成🙏

## 分支说明

多分支维护成本过高，多余分支将被清理或停止维护，计划合成为一个 cookiecutter 新仓库，在此之前,
请注意查看分支下相关说明

### 异步：

#### async -> master

```text
fastapi + sqlalchemy + alembic + asyncmy + aioredis

✨: 邮箱验证码登录
⚠️: 停止维护
```

#### async -> async-CRUDBase

```text
fastapi + sqlalchemy + alembic + asyncmy + aioredis + APScheduler

✨: 在 master 分支基础上扩展，集成 CRUD 封装和 APScheduler 定时任务
```

#### async -> async-Plus

```text
fastapi + sqlalchemy + alembic + asyncmy + aioredis + APScheduler + PyCasbin

✨: 在 async-CRUDBase 分支基础上扩展，集成来自 PyCasbin 的 RBAC 鉴权
```

### 同步：

#### sync -> sync

```text
fastapi + sqlalchemy + alembic + pymysql + redis

✨: 图片验证码登录
⚠️: 停止维护
```

#### sync -> sync-CRUDBase

```text
fastapi + sqlalchemy + alembic + pymysql + redis + APScheduler

✨: 在 sync 分支基础上扩展，集成 CRUD 封装和 APScheduler 定时任务
```

#### sync -> sync-Plus

```text
fastapi + sqlalchemy + alembic + pymysql + redis + APScheduler + PyCasbin

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
