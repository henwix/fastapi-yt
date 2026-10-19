from dataclasses import dataclass


@dataclass
class PurgeDeletedChannelsUseCase:
    async def execute(self): ...
