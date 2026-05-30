from pwdlib import PasswordHash

from app.application.common.password_hasher import IPasswordHasher

_password_hasher = PasswordHash.recommended()
_dummy_password = 'not-a-real-password'
_dummy_hash = _password_hasher.hash(password=_dummy_password)


class PwdlibPasswordHasher(IPasswordHasher):
    def get_password_hash(self, password: str) -> str:
        return _password_hasher.hash(password=password)

    def verify_password_hash(self, password: str, hash: str | None = None) -> bool:
        return _password_hasher.verify(password=password, hash=hash if hash is not None else _dummy_hash)
