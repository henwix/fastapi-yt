from uuid import uuid7

import pytest
from dishka.async_container import AsyncContainer
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.auth.use_cases.reset_channel_password_confirm import ResetChannelPasswordConfirmUseCase
from app.domain.auth.exceptions import ChannelInvalidEmailCodeError, ChannelInvalidEmailUIDError
from app.domain.auth.service import IAuthService
from app.domain.channels.exceptions import ChannelNotFoundByIdError
from app.utils.base64url import base64url_encode
from tests.factories.commands.auth import ResetChannelPasswordConfirmCommandFactory
from tests.factories.models.channels import ChannelORMFactory

_password_hasher = PasswordHash.recommended()


@pytest.mark.asyncio
async def test_reset_channel_password_confirm_returns_none_if_password_updated(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(ResetChannelPasswordConfirmUseCase)
        auth_service = await di.get(IAuthService)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(session=session)
        code = await auth_service.create_reset_password_code(channel_id=db_channel.id)
        command = ResetChannelPasswordConfirmCommandFactory.build(
            code=code, uid=base64url_encode(value=str(db_channel.id))
        )

        assert not _password_hasher.verify(password=command.new_password, hash=db_channel.password_hash)

        result = await use_case.execute(command=command)

        assert result is None
        assert _password_hasher.verify(password=command.new_password, hash=db_channel.password_hash)


@pytest.mark.asyncio
@pytest.mark.parametrize('expected_uid', ['InRlc3Rfc3RyaW5nIg', '123123', 'aaaaa', 'sjlfkahf', 'IjExMjMxMjMxMjMi'])
async def test_reset_channel_password_confirm_raises_error_if_invalid_channel_uid(
    container: AsyncContainer,
    expected_uid: str,
):
    async with container() as di:
        use_case = await di.get(ResetChannelPasswordConfirmUseCase)

        command = ResetChannelPasswordConfirmCommandFactory.build(uid=expected_uid)

        with pytest.raises(ChannelInvalidEmailUIDError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_reset_channel_password_confirm_raises_error_if_code_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(ResetChannelPasswordConfirmUseCase)

        channel_id = uuid7()

        command = ResetChannelPasswordConfirmCommandFactory.build(
            code='test_code', uid=base64url_encode(value=str(channel_id))
        )

        with pytest.raises(ChannelInvalidEmailCodeError) as e:
            await use_case.execute(command=command)

        assert e.value.code == command.code
        assert e.value.channel_id == channel_id
        assert e.value.reason == 'reset_password_code_not_found'


@pytest.mark.asyncio
async def test_reset_channel_password_confirm_raises_error_if_code_mismatch(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(ResetChannelPasswordConfirmUseCase)
        auth_service = await di.get(IAuthService)

        channel_id = uuid7()

        await auth_service.create_reset_password_code(channel_id=channel_id)
        command = ResetChannelPasswordConfirmCommandFactory.build(
            code='test_code', uid=base64url_encode(value=str(channel_id))
        )

        with pytest.raises(ChannelInvalidEmailCodeError) as e:
            await use_case.execute(command=command)

        assert e.value.code == command.code
        assert e.value.channel_id == channel_id
        assert e.value.reason == 'reset_password_code_mismatch'


@pytest.mark.asyncio
async def test_reset_channel_password_confirm_raises_error_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(ResetChannelPasswordConfirmUseCase)
        auth_service = await di.get(IAuthService)

        channel_id = uuid7()

        code = await auth_service.create_reset_password_code(channel_id=channel_id)
        command = ResetChannelPasswordConfirmCommandFactory.build(
            code=code, uid=base64url_encode(value=str(channel_id))
        )

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)
