import parse
import typing
import logging
import discord_typings
from .callback import InteractionCallback

logger = logging.getLogger(__name__)

CallbackT = typing.TypeVar("CallbackT", bound=typing.Type)

class InteractionHandler:
    def __init__(self) -> None:
        self.handlers: dict[parse.Parser, InteractionCallback] = {}

    async def process_interaction(self, interaction: discord_typings.InteractionData) -> None:
        custom_id = interaction["data"].get("custom_id")
        command_name = interaction["data"].get("name")

        interaction_key = custom_id or command_name
        
        assert interaction_key is not None, "Interaction key was None?"

        result = self.get_handler_by_interaction_key(interaction_key)

        if result is None:
            logger.warning(f"Received unhandled interaction with key: {interaction_key}")
            return

        handler, args = result
        
        try:
            await handler.run(interaction, args)
        except Exception as error:
            # If this fails, you deserve it
            await handler.on_error(interaction, args, error)

    def get_handler_by_interaction_key(self, key: str) -> tuple[InteractionCallback, parse.Result] | None:
        for handler_format_key, handler in self.handlers.items():
            result = handler_format_key.parse(key)
            
            # Parse does not use overloads, but unless evalute_results=False is given to the function, it will never be a match
            result = typing.cast(parse.Result, result)

            if result is None:
                continue

            return handler, result

    def add_handler(self, callback: InteractionCallback) -> None:
        if callback.FORMAT == "":
            raise ValueError("Missing FORMAT")
        compiled_format = parse.compile(callback.FORMAT)
        self.handlers[compiled_format] = callback


