import re
import time

import pytest

from app.exceptions import BadCookieSignature
from app.utils import generate_secure_cookie, validate_secure_cookie


def test_generate_secure_cookie(app):
    """
    Test the generate_secure_cookie function
    """
    with app.app_context():
        plex_auth_cookie_data = {
            "plex_auth_token": "test",
        }

        plexauth_cookie = generate_secure_cookie(plex_auth_cookie_data, salt="plexauth")
        assert isinstance(plexauth_cookie, str)

        # test valid care with max age
        assert isinstance(
            validate_secure_cookie(plexauth_cookie, salt="plexauth", max_age=15552000),
            dict,
        )
        assert (
            validate_secure_cookie(plexauth_cookie, salt="plexauth", max_age=2)
            == plex_auth_cookie_data
        )

        # test expired cookie scenario
        time.sleep(1)
        with pytest.raises(BadCookieSignature) as exc_info:
            validate_secure_cookie(plexauth_cookie, salt="plexauth", max_age=0.01)

        # Check the exception message (optional)
        assert str(exc_info.value) == (
            "Signature validation failed for cookie:" " Signature age 1 > 0.01 seconds"
        )

        # test invalid salt scenario
        with pytest.raises(BadCookieSignature) as exc_info:
            validate_secure_cookie(plexauth_cookie, salt="invalid", max_age=15552000)

        # Check the exception message (optional)
        assert re.match(
            r"Signature validation failed for cookie: Signature b'\S+' does not match",
            str(exc_info.value),
        )
