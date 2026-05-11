from config import settings


class SQLQueries:
    """Коллекция SQL запросов для WordPress БД"""

    GET_POST_BY_ID = f"""
        SELECT ID, post_title, post_content, post_status, post_author, post_date, post_modified
        FROM {settings.table_posts}
        WHERE ID = %s
    """

    COUNT_POSTS_BY_TITLE = f"""
        SELECT COUNT(*) as post_count 
        FROM {settings.table_posts}
        WHERE post_title = %s
    """

    GET_USER_BY_ID = f"""
        SELECT ID, user_login, user_email, user_nicename 
        FROM {settings.table_users}
        WHERE ID = %s
    """

    GET_USER_BY_EMAIL = f"""
        SELECT ID, user_login, user_email 
        FROM {settings.table_users}
        WHERE user_email = %s
    """

    COUNT_USERS_BY_EMAIL = f"""
        SELECT COUNT(*) as user_count 
        FROM {settings.table_users}
        WHERE user_email = %s
    """

    GET_USER_META = f"""
        SELECT meta_key, meta_value 
        FROM {settings.table_usermeta}
        WHERE user_id = %s AND meta_key IN %s
    """

    GET_USER_CAPABILITIES = f"""
        SELECT meta_value 
        FROM {settings.table_usermeta}
        WHERE user_id = %s AND meta_key = 'wp_capabilities'
    """
