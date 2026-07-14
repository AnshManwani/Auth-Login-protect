from flask import Flask
from dotenv import load_dotenv
from app.postgres_repository import PostgresItemRepository
from app.user_repository import PostgresUserRepository
from app.service import ItemService
from app.auth_service import AuthService
from app.routes import register_routes

load_dotenv()


def create_app():
    app = Flask(__name__)
    repository = PostgresItemRepository()
    user_repository = PostgresUserRepository()
    service = ItemService(repository)
    auth_service = AuthService(user_repository)
    register_routes(app, service, auth_service)
    return app