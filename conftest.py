import logging
import allure
import pymysql
import pytest
import requests
from requests.auth import HTTPBasicAuth

from api.clients.posts_client import PostsClient
from api.clients.comments_client import CommentsClient
from config import settings
from db.db_client import DBClient
from faker import Faker

fake = Faker()
logger = logging.getLogger(__name__)


def pytest_configure(config):
    """Настройка логирования"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("tests.log", encoding="utf-8")],
    )


# --- СЕССИИ ---

@pytest.fixture(scope="session")
def api_session():
    """Сессия с авторизацией (Basic Auth)"""
    session = requests.Session()
    session.auth = HTTPBasicAuth(settings.wp_api_user, settings.wp_api_pass)
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="session")
def unauth_session():
    """Сессия БЕЗ авторизации (для негативных кейсов)"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


# --- КЛИЕНТЫ ---

@pytest.fixture(scope="session")
def posts_client(api_session):
    return PostsClient(api_session, settings.api_posts_endpoint)


@pytest.fixture(scope="session")
def comments_client(api_session):
    return CommentsClient(api_session, settings.api_comments_endpoint)


@pytest.fixture(scope="session")
def unauth_posts_client(unauth_session):
    return PostsClient(unauth_session, settings.api_posts_endpoint)


@pytest.fixture(scope="session")
def unauth_comments_client(unauth_session):
    return CommentsClient(unauth_session, settings.api_comments_endpoint)


# --- БАЗА ДАННЫХ ---

@pytest.fixture(scope="function")
def db_client():
    """Клиент БД"""
    connection = pymysql.connect(
        **settings.db_connection_params,
        cursorclass=pymysql.cursors.DictCursor
    )
    client = DBClient(connection)
    yield client
    connection.close()


# --- PRECONDITIONS (ПОДГОТОВКА ДАННЫХ) ---

@pytest.fixture(scope="function")
def create_test_post(posts_client):
    """Создает пост и удаляет его после теста"""
    payload = {
        "title": f"Test Post {fake.uuid4()}",
        "content": "Content for testing",
        "status": "publish"
    }
    response = posts_client.create_post(**payload)
    post_id = response.json().get("id")

    yield post_id

    try:
        posts_client.delete_post(post_id, force=True)
    except Exception:
        pass


@pytest.fixture(scope="function")
def create_test_comment(comments_client, create_test_post):
    """Создает комментарий к тестовому посту"""
    post_id = create_test_post
    response = comments_client.create_comment(
        post_id=post_id,
        content="Initial Comment for Testing",
        author_name="Test Bot",
        author_email="bot@test.com"
    )
    comment_id = response.json().get("id")

    yield comment_id

    try:
        comments_client.delete_comment(comment_id, force=True)
    except Exception:
        pass


# --- CLEANUP (СПИСКИ НА УДАЛЕНИЕ) ---

@pytest.fixture(scope="function")
def post_cleanup(posts_client):
    """Список для ID постов, которые надо удалить после теста"""
    ids = []
    yield ids
    for p_id in ids:
        try:
            posts_client.delete_post(p_id, force=True)
        except:
            pass


@pytest.fixture(scope="function")
def comment_cleanup(comments_client):
    """Список для ID комментариев, которые надо удалить после теста"""
    ids = []
    yield ids
    for c_id in ids:
        try:
            comments_client.delete_comment(c_id, force=True)
        except:
            pass

@pytest.fixture(scope="function")
def new_post_cleanup(post_cleanup):
    return post_cleanup

@pytest.fixture(scope="session")
def unauthorized_posts_client(unauth_posts_client):
    return unauth_posts_client

@pytest.fixture(scope="session")
def unauthorized_comments_client(unauth_comments_client):
    return unauth_comments_client
