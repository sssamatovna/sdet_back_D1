import allure
from faker import Faker

from db.queries import SQLQueries
from utils.allure_helpers import attach_db_result, attach_api_response

fake = Faker()

@allure.title("TC-001: Создание поста через API")
@allure.description("Проверяем, что пост создаётся через API и правильно записывается в БД")
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("Posts")
@allure.story("CRUD Operations")
@allure.tag("positive", "api", "database")
def test_tc001_create_post(posts_client, db_client, new_post_cleanup):

    title = fake.sentence()
    content = "Это тестовый контент, созданный с помощью API"
    status = "publish"

    with allure.step(f"Отправить POST запрос на создание поста (title='{title}')"):
        response = posts_client.create_post(title=title, content=content, status=status)
        attach_api_response(response, expected_status=201)
        assert ( response.status_code == 201), f"Ожидалось 201, получен {response.status_code}"

    post_id = response.json()["id"]
    new_post_cleanup.append(post_id)

    with (allure.step(f"Проверить данные поста {post_id} в БД")):
        db_post = db_client.execute_query(SQLQueries.GET_POST_BY_ID, (post_id,))
        attach_db_result(db_post, expected_values={"post_title": title, "post_status": status})

        assert (db_post["post_title"] == title), f"Заголовок не совпадает. Ожидалось: '{title}', в БД: '{db_post['post_title']}'"
        assert (db_post["post_content"] == content), f"Заголовок не совпадает. Ожидалось: '{content}', в БД: '{db_post['post_content']}'"
        assert (db_post["post_status"] == status), f"Статус не совпадает. Ожидалось: '{status}', в БД: '{db_post['post_status']}'"


@allure.title("TC-002: Редактирование заголовка поста")
@allure.description("Проверяем, что заголовок поста обновляется через API и отражается в БД")
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("Posts")
@allure.story("CRUD Operations")
@allure.tag("positive", "api", "database")
def test_tc002_update_post_title(posts_client, db_client, create_test_post):

    post_id = create_test_post
    new_title = f"Updated: {fake.sentence()}"

    with allure.step(f"Обновить заголовок поста {post_id} на '{new_title}'"):
        response = posts_client.update_post(post_id, {"title": new_title})
        attach_api_response(response, expected_status=200)
        assert (response.status_code == 200), f"Ожидалось 200, получен {response.status_code}"

    with allure.step("Проверить изменения в БД"):
        db_post = db_client.execute_query(SQLQueries.GET_POST_BY_ID, (post_id,))

        assert ( db_post["post_title"] == new_title), f"Заголовок не совпадает. Ожидалось: '{new_title}', в БД: '{db_post["post_title"]}'"


@allure.title("TC-003: Удаление поста через API")
@allure.description("Проверяем, что пост удаляется через API и переходит в статус 'trash' в БД")
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("Posts")
@allure.story("CRUD Operations")
@allure.tag("positive", "api", "database")
def test_tc03_delete_post(posts_client, db_client, create_test_post):

    post_id = create_test_post

    with allure.step(f"Отправить DELETE запрос на /wp/v2/posts/{post_id}"):
        response = posts_client.delete_post(post_id, force=False)
        attach_api_response(response, expected_status=200)
        assert (response.status_code == 200), f"Ожидался статус 200 OK, получен {response.status_code}"

    with allure.step("Проверить удаление данных поста в БД"):
        db_post = db_client.execute_query(SQLQueries.GET_POST_BY_ID, (post_id,))

        attach_db_result(
            result=db_post,
            expected_values={"post_status": "trash"},
            name="Post Status After Delete",
        )

        assert db_post is not None, f"Пост ID={post_id} не найден в БД"
        assert (db_post["post_status"] == "trash"), f"Ожидался статус 'trash', в БД: '{db_post['post_status']}'"