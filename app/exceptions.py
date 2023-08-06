import itsdangerous


class CookieNotFound(KeyError):
    pass


class BadCookieSignature(itsdangerous.BadSignature):
    pass
