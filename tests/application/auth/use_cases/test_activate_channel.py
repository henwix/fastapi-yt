import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.auth.use_cases.activate_channel import ActivateChannelUseCase
from app.domain.auth.exceptions import ChannelAlreadyActivatedError, ChannelInvalidEmailCodeError
from app.domain.auth.service import IAuthService
from app.domain.channels.exceptions import ChannelNotFoundByIdError
from tests.factories.commands.auth import ActivateChannelCommandFactory
from tests.factories.models.channels import ChannelORMFactory


@pytest.mark.asyncio
async def test_activate_channel_returns_none_if_activated(container: AsyncContainer):
    async with container() as di:
        auth_service = await di.get(IAuthService)
        use_case = await di.get(ActivateChannelUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(session=session, is_active=False)
        code = await auth_service.create_activation_code(channel_id=db_channel.id)
        command = ActivateChannelCommandFactory.build(current_channel_id=db_channel.id, code=code)

        assert not db_channel.is_active

        result = await use_case.execute(command=command)

        assert result is None
        assert db_channel.is_active


@pytest.mark.asyncio
async def test_activate_channel_raises_error_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(ActivateChannelUseCase)
        command = ActivateChannelCommandFactory.build()

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_activate_channel_raises_error_if_channel_is_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(ActivateChannelUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(session=session)
        command = ActivateChannelCommandFactory.build(current_channel_id=db_channel.id)

        with pytest.raises(ChannelAlreadyActivatedError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_activate_channel_raises_error_if_activation_code_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(ActivateChannelUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(session=session, is_active=False)
        command = ActivateChannelCommandFactory.build(current_channel_id=db_channel.id)

        with pytest.raises(ChannelInvalidEmailCodeError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == db_channel.id
        assert e.value.code == command.code
        assert e.value.reason == 'reset_password_code_not_found'


@pytest.mark.asyncio
async def test_activate_channel_raises_error_if_activation_code_mismatch(container: AsyncContainer):
    async with container() as di:
        auth_service = await di.get(IAuthService)
        use_case = await di.get(ActivateChannelUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(session=session, is_active=False)
        await auth_service.create_activation_code(channel_id=db_channel.id)
        command = ActivateChannelCommandFactory.build(current_channel_id=db_channel.id)

        with pytest.raises(ChannelInvalidEmailCodeError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == db_channel.id
        assert e.value.code == command.code
        assert e.value.reason == 'reset_password_code_mismatch'
