# The MIT License (MIT)
#
# Copyright (c) 2022-present nextcore developers
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import asyncio
from os import environ
from typing import cast
import random

from discord_typings import InteractionData
from nextcore.gateway import ShardManager
from nextcore.http import BadRequestError, BotAuthentication, HTTPClient, Route
import parse
from shitpost.callback import InteractionCallback

from shitpost.handler import InteractionHandler

# Constants
AUTHENTICATION = BotAuthentication(environ["TOKEN"])
APPLICATION_ID = environ["BOT_ID"]

# Intents are a way to select what intents Discord should send to you.
# For a list of intents see https://discord.dev/topics/gateway#gateway-intents
INTENTS = 0 # Guild messages and message content intents.


# Create a HTTPClient and a ShardManager.
# A ShardManager is just a neat wrapper around Shard objects.
http_client = HTTPClient()
shard_manager = ShardManager(AUTHENTICATION, INTENTS, http_client)
interaction_handler = InteractionHandler()


@shard_manager.event_dispatcher.listen("INTERACTION_CREATE")
async def on_interaction(interaction: InteractionData):
    await interaction_handler.process_interaction(interaction)

# Interactions
class ShowButtonCommand(InteractionCallback):
    FORMAT = "show-button"

    async def run(self, interaction: InteractionData, args: parse.Result):
        del args

        custom_id = HelloButtonCommand.create_custom_id(random_number=random.randint(0,10))

        data = {
            "type": 4,
            "data": {
                "content": "Hello",
                "components": [
                    {
                        "type": 1,
                        "components": [
                            {
                                "type": 2,
                                "label": "Click me",
                                "style": 1,
                                "custom_id": custom_id
                            }
                        ]
                    }
                ]
            }
        }

        route = Route("POST", "/interactions/{interaction_id}/{interaction_token}/callback", interaction_id=interaction["id"], interaction_token = interaction["token"])
        try:
            await http_client.request(route, json=data, rate_limit_key=None)
        except BadRequestError as e:
            print(await e.response.json())

class HelloButtonCommand(InteractionCallback):
    FORMAT = "hello-button:{random_number}"

    async def run(self, interaction: InteractionData, args: parse.Result):
        number = args["random_number"]
        route = Route("POST", "/interactions/{interaction_id}/{interaction_token}/callback", interaction_id=interaction["id"], interaction_token = interaction["token"])
        await http_client.request(route, json={"type": 4, "data": {"content": f"Hello! Your random number was {number}"}}, rate_limit_key=None)



async def main():
    await http_client.setup()

    # This should return once all shards have started to connect.
    # This does not mean they are connected.
    await shard_manager.connect()

    # Register commands. This should ideally only be done once updating, however this is a demo so it is fine.
    route = Route("PUT", "/applications/{application_id}/commands", application_id=APPLICATION_ID)
    await http_client.request(route, rate_limit_key=AUTHENTICATION.rate_limit_key, headers=AUTHENTICATION.headers, json=[
        {
            "name": "show-button",
            "description": "Shows a button!"
        }
    ])

    # Register handlers
    interaction_handler.add_handler(ShowButtonCommand())
    interaction_handler.add_handler(HelloButtonCommand())

    # Raise a error and exit whenever a critical error occurs
    (error,) = await shard_manager.dispatcher.wait_for(lambda: True, "critical")

    raise cast(Exception, error)


asyncio.run(main())
