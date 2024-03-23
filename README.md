# FastAPI SQLAlchemy MySQL

[![Static Badge](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)

> [!TIP]
> 此仓库是我们构建的 FastAPI 基础架构便捷版，完整版请查看：
> [fastapi_best_architecture](https://github.com/fastapi-practices/fastapi_best_architecture)

## 特征

- [x] FastAPI
- [x] Async design
- [x] Restful API
- [x] SQLAlchemy 2.0
- [x] Pydantic 2.0
- [x] Docker
- [ ] ......

## 本地开发

* Python 3.10+
* Mysql 8.0+
* Redis 推荐最新稳定版

1. 安装依赖项

   ```shell
   pip install -r requirements.txt
   ```

2. 创建一个数据库 `fsm`, 选择 utf8mb4 编码
3. 安装启动 Redis
4. 创建一个 `.env` 文件

   ```shell
   touch .env
   cp .env.example .env
   ```

5. 按需修改配置文件 `core/conf.py` 和 `.env`
6. 数据库迁移 [alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

    ```shell
    # 生成迁移文件
    alembic revision --autogenerate
    
    # 执行迁移
    alembic upgrade head
    ```

7. 执行 main.py 文件启动服务
8. 浏览器访问: http://127.0.0.1:8000/api/v1/docs

---

### Docker

> [!WARNING]
>
> 默认端口冲突：8000，3306，6379
>
> 建议在部署前关闭本地服务：mysql，redis...

1. 进入 `docker-compose.yml` 文件所在目录，创建环境变量文件 `.env`

    ```shell
    cd deploy/docker-compose/
   
    cp .env.server ../../.env
    ```

2. 执行一键启动命令

    ```shell
    docker-compose up -d --build
    ```

3. 等待命令自动完成
4. 浏览器访问：http://127.0.0.1:8000/api/v1/docs

## 互动

[WeChat / QQ](https://github.com/wu-clan)

## 赞助

如果此项目能够帮助到你，你可以赞助作者一些咖啡豆表示鼓励：[:coffee: Sponsor :coffee:](https://wu-clan.github.io/sponsor/)

## 许可证

本项目根据 MIT 许可证的条款进行许可
