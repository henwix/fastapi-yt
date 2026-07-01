import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.channels.use_cases.set_password import SetChannelPasswordUseCase
from app.application.common.interfaces.password_hasher import IPasswordHasher
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from tests.factories.commands.channels import SetChannelPasswordCommandFactory
from tests.factories.models.channels import ChannelORMFactory


@pytest.mark.asyncio
async def test_set_password_returns_none_if_password_updated(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(SetChannelPasswordUseCase)
        session = await di.get(AsyncSession)
        password_hasher = await di.get(IPasswordHasher)
        db_channel = await ChannelORMFactory.create(session=session, is_active=True)
        old_password_hash = db_channel.password_hash
        command = SetChannelPasswordCommandFactory.build(current_channel_id=db_channel.id)

        use_case_result = await use_case.execute(command=command)

        assert use_case_result is None
        assert db_channel.password_hash != old_password_hash
        assert password_hasher.verify_password_hash(password=command.new_password, hash=db_channel.password_hash)


@pytest.mark.asyncio
async def test_set_password_raises_error_if_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(SetChannelPasswordUseCase)
        session = await di.get(AsyncSession)
        db_channel = await ChannelORMFactory.create(session=session, is_active=False)
        command = SetChannelPasswordCommandFactory.build(current_channel_id=db_channel.id)

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_set_password_raises_error_if_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(SetChannelPasswordUseCase)
        command = SetChannelPasswordCommandFactory.build()

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)
