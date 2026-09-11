from abc import ABC, abstractmethod


class IAuthCodeService(ABC):
    @abstractmethod
    def build_activation_url(self, code: str) -> str: ...

    @abstractmethod
    def build_reset_password_confirm_url(self, code: str, uid: str) -> str: ...

    @abstractmethod
    def build_set_email_confirm_url(self, code: str) -> str: ...

    @abstractmethod
    async def create_activation_code(self, channel_id: UUID) -> str: ...

    @abstractmethod
    async def create_reset_password_code(self, channel_id: UUID) -> str: ...

    @abstractmethod
    async def create_set_email_code(self, channel_id: UUID, new_email: str) -> str: ...

    @abstractmethod
    async def validate_activation_code(self, channel_id: UUID, code: str) -> None: ...

    @abstractmethod
    async def validate_reset_password_code(self, channel_id: UUID, code: str) -> str: ...

    @abstractmethod
    async def validate_set_email_code(self, channel_id: UUID, code: str) -> str: ...
