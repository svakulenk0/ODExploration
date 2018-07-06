from opsdroid.matchers import match_regex
import logging
import random

def setup(opsdroid):
    logging.debug("Loaded ODExploration skill")

@match_regex(r'.*')
async def hello2(opsdroid, config, message):
    text = random.choice(["Yes!"])
    await message.respond(text)
