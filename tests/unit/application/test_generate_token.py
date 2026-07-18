"""
Tests de GenerateTokenUseCase — sin DB, usando mock de UserRepository.
"""

import re
from unittest.mock import MagicMock

import pytest

from app.application.user.edit import UserNotFoundError
from app.application.user.generate_token import GenerateTokenUseCase
from tests.factories.user_factory import UserFactory


@pytest.fixture
def repo():
    return MagicMock()


@pytest.fixture
def user():
    return UserFactory.build(id=1, ws_token=None)


def test_generate_token_updates_ws_token(repo, user):
    repo.find_by_id.return_value = user
    repo.save.return_value = user

    use_case = GenerateTokenUseCase(repo)
    token = use_case.execute(1)

    assert token is not None
    assert len(token) > 0
    assert user.ws_token == token


def test_generate_token_token_is_sha512_format(repo, user):
    repo.find_by_id.return_value = user
    repo.save.return_value = user

    use_case = GenerateTokenUseCase(repo)
    token = use_case.execute(1)

    # SHA-512 hexdigest = 128 hex chars
    assert len(token) == 128
    assert re.fullmatch(r"[0-9a-f]{128}", token) is not None


def test_generate_token_saves_via_repository(repo, user):
    repo.find_by_id.return_value = user
    repo.save.return_value = user

    use_case = GenerateTokenUseCase(repo)
    use_case.execute(1)

    repo.save.assert_called_once_with(user)


def test_generate_token_raises_when_user_not_found(repo):
    repo.find_by_id.return_value = None

    use_case = GenerateTokenUseCase(repo)
    with pytest.raises(UserNotFoundError):
        use_case.execute(999)
