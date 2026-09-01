import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.auth.use_cases.set_channel_email_confirm import SetChannelEmailConfirmUseCase
from app.domain.auth.exceptions import ChannelInvalidEmailCodeError
from app.domain.auth.service import IAuthService
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from tests.factories.commands.auth import SetChannelEmailConfirmCommandFactory
from tests.factories.models.channels import ChannelORMFactory


@pytest.mark.asyncio
async def test_set_channel_email_confirm_returns_none_if_email_confirmed(container: AsyncContainer):
    async with container() as di:
        expected_new_email = 'testnewemail@test.com'
        use_case = await di.get(SetChannelEmailConfirmUseCase)
        session = await di.get(AsyncSession)
        auth_service = await di.get(IAuthService)

        db_channel = await ChannelORMFactory.create(session=session)

        code = await auth_service.create_set_email_code(channel_id=db_channel.id, new_email=expected_new_email)
        command = SetChannelEmailConfirmCommandFactory.build(current_channel_id=db_channel.id, code=code)

        result = await use_case.execute(command=command)

        assert result is None
        assert db_channel.email == expected_new_email


@pytest.mark.asyncio
async def test_set_channel_email_confirm_raises_error_if_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(SetChannelEmailConfirmUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(session=session, is_active=False)

        command = SetChannelEmailConfirmCommandFactory.build(current_channel_id=db_channel.id)

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_set_channel_email_confirm_raises_error_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(SetChannelEmailConfirmUseCase)

        command = SetChannelEmailConfirmCommandFactory.build()

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_set_channel_email_confirm_raises_error_if_code_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(SetChannelEmailConfirmUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(session=session)

        command = SetChannelEmailConfirmCommandFactory.build(current_channel_id=db_channel.id)

        with pytest.raises(ChannelInvalidEmailCodeError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == db_channel.id
        assert e.value.code == command.code
        assert e.value.reason == 'set_email_code_not_found'


@pytest.mark.asyncio
async def test_set_channel_email_confirm_raises_error_if_code_mismatch(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(SetChannelEmailConfirmUseCase)
        session = await di.get(AsyncSession)
        auth_service = await di.get(IAuthService)

        db_channel = await ChannelORMFactory.create(session=session)
        await auth_service.create_set_email_code(channel_id=db_channel.id, new_email='test@test.com')

        command = SetChannelEmailConfirmCommandFactory.build(current_channel_id=db_channel.id)

        with pytest.raises(ChannelInvalidEmailCodeError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == db_channel.id
        assert e.value.code == command.code
        assert e.value.reason == 'set_email_code_mismatch'
