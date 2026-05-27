from dataclasses import dataclass

from pwdlib import PasswordHash

from app.domain.common.interfaces.password_hasher import IPasswordHasher


@dataclass
class PwdlibPasswordHasher(IPasswordHasher):
    password_hasher: PasswordHash = PasswordHash.recommended()

    def get_password_hash(self, password: str) -> str:
        return self.password_hasher.hash(password=password)

    def verify_password_hash(self, password: str, hash: str) -> bool:
        return self.password_hasher.verify(password=password, hash=hash)
