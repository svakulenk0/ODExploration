from opsdroid.matchers import match_regex
import logging
import random

from .dialog_agent import DialogAgent

chatbot = DialogAgent()


def setup(opsdroid):
    logging.debug("Loaded ODExploration skill")


@match_regex(r'.*')
async def exploreOD(opsdroid, config, message):
    chatbot.history = []
    chatbot.goal = []
    # start exploration
    text, actions = chatbot.chat(start=True)
    await message.respond(text)
