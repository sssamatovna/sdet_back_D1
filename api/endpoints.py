class APIEndpoints:
    """Вспомогательный класс для формирования относительных путей."""

    POSTS = ""
    COMMENTS = ""

    @staticmethod
    def post_by_id(post_id: int) -> str:
        return f"{post_id}"

    @staticmethod
    def comment_by_id(comment_id: int) -> str:
        return f"{comment_id}"