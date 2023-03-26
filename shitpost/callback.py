import discord_typings
import parse
import logging
import typing

logger = logging.getLogger(__name__)

class InteractionCallback:
    FORMAT: str = ""

    @classmethod
    def create_custom_id(cls, *args, **kwargs):
        return cls.FORMAT.format(*args, **kwargs)

    async def run(self, interaction: discord_typings.InteractionData, args: parse.Result):
        ...
    async def on_error(self, interaction: discord_typings.InteractionData, args: parse.Result, error: BaseException):
        logger.exception("Error while handling interaction")
        
