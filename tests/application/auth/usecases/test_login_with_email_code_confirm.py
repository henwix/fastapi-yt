from uuid import uuid7

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.auth.usecases import LoginWithEmailCodeConfirmUseCase
from app.application.common.dto.jwt import JWTTokens
from app.application.common.interfaces.security import IAuthCodeService, IJWTService
from app.domain.auth.exceptions import ChannelInvalidEmailCodeError, ChannelInvalidEmailUIDError
from app.domain.channels.exceptions import ChannelNotFoundByIdError
from app.utils.base64url import base64url_encode
from tests.factories.commands.auth import LoginWithEmailCodeConfirmCommandFactory
from tests.factories.models.channels import ChannelORMFactory


@pytest.mark.asyncio
@pytest.mark.parametrize('has_password', [True, False])
async def test_login_with_email_code_confirm_returns_tokens_if_code_and_uid_correct(
    container: AsyncContainer,
    has_password: bool,
):
    async with container() as di:
        use_case = await di.get(LoginWithEmailCodeConfirmUseCase)
        jwt_service = await di.get(IJWTService)
        auth_code_service = await di.get(IAuthCodeService)
        session = await di.get(AsyncSession)

        if has_password:
            channel = await ChannelORMFactory.create(session=session)
        else:
            channel = await ChannelORMFactory.create(session=session, password_hash=None)

        code = await auth_code_service.create_login_email_code(channel_id=channel.id)
        uid = base64url_encode(value=str(channel.id))
        command = LoginWithEmailCodeConfirmCommandFactory.build(code=code, uid=uid)

        tokens = await use_case.execute(command=command)

        assert isinstance(tokens, JWTTokens)
        decoded_access = jwt_service.decode_access_token(token=tokens.access.token)
        decoded_refresh = jwt_service.decode_refresh_token(token=tokens.refresh.token)

        assert decoded_access.jti is None
        assert decoded_access.token_type == 'access'
        assert decoded_access.sub == str(channel.id)

        assert decoded_refresh.jti is not None
        assert decoded_refresh.token_type == 'refresh'
        assert decoded_refresh.sub == str(channel.id)


@pytest.mark.asyncio
@pytest.mark.parametrize('expected_uid', ['123', 'akjshfaf', 'AJKDHAF', 'VVASD123', 'test', '1', '', ' '])
async def test_login_with_email_code_confirm_raises_error_if_uid_invalid(
    container: AsyncContainer,
    expected_uid: str,
):
    async with container() as di:
        use_case = await di.get(LoginWithEmailCodeConfirmUseCase)

        command = LoginWithEmailCodeConfirmCommandFactory.build(uid=expected_uid)

        with pytest.raises(ChannelInvalidEmailUIDError) as e:
            await use_case.execute(command=command)

        assert e.value.uid == expected_uid


@pytest.mark.asyncio
async def test_login_with_email_code_confirm_raises_error_if_code_not_found(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(LoginWithEmailCodeConfirmUseCase)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create(session=session)

        uid = base64url_encode(value=str(channel.id))
        command = LoginWithEmailCodeConfirmCommandFactory.build(uid=uid)

        with pytest.raises(ChannelInvalidEmailCodeError) as e:
            await use_case.execute(command=command)

        assert e.value.code == command.code
        assert e.value.channel_id == channel.id
        assert e.value.reason == 'login_email_code_not_found'


@pytest.mark.asyncio
async def test_login_with_email_code_confirm_raises_error_if_code_mismatch(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(LoginWithEmailCodeConfirmUseCase)
        auth_code_service = await di.get(IAuthCodeService)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create(session=session)

        uid = base64url_encode(value=str(channel.id))
        await auth_code_service.create_login_email_code(channel_id=channel.id)
        command = LoginWithEmailCodeConfirmCommandFactory.build(uid=uid)

        with pytest.raises(ChannelInvalidEmailCodeError) as e:
            await use_case.execute(command=command)

        assert e.value.code == command.code
        assert e.value.channel_id == channel.id
        assert e.value.reason == 'login_email_code_mismatch'


@pytest.mark.asyncio
async def test_login_with_email_code_confirm_raises_error_if_channel_not_found(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(LoginWithEmailCodeConfirmUseCase)
        auth_code_service = await di.get(IAuthCodeService)

        channel_id = uuid7()

        code = await auth_code_service.create_login_email_code(channel_id=channel_id)
        uid = base64url_encode(value=str(channel_id))
        command = LoginWithEmailCodeConfirmCommandFactory.build(code=code, uid=uid)

        with pytest.raises(ChannelNotFoundByIdError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == channel_id
