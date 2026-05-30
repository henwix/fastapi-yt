from pwdlib import PasswordHash

from app.application.common.password_hasher import IPasswordHasher


class PwdlibPasswordHasher(IPasswordHasher):
    def __init__(self) -> None:
        self.password_hasher: PasswordHash = PasswordHash.recommended()

    def get_password_hash(self, password: str) -> str:
        return self.password_hasher.hash(password=password)

    def verify_password_hash(self, password: str, hash: str) -> bool:
        return self.password_hasher.verify(password=password, hash=hash)
