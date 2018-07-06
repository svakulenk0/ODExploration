from opsdroid.matchers import match_regex
import logging
import random

from .dialog_agent import DialogAgent

chatbot = DialogAgent()


def setup(opsdroid):
    logging.debug("Loaded ODExploration skill")


@match_regex(r'browse')
async def exploreOD(opsdroid, config, message):
    chatbot.history = []
    chatbot.goal = []
    # start exploration
    text, actions = chatbot.chat(start=True)
    print(text)
    await message.respond(text)


@match_regex(r'search .*')
async def searchOD(opsdroid, config, message):
    request = message
    print request
    text, actions = chatbot.search(request)
    print(text)
    await message.respond(text)
