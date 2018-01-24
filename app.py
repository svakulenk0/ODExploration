'''
svakulenko
22 Dec 2017

Flas web app for chatbot interface based on https://github.com/chamkank/flask-chatterbot
'''
import json
from flask import Flask, render_template, request

from dialog_agent import DialogAgent

app = Flask(__name__)

chatbot = DialogAgent()


@app.route("/")
def home():
    # start exploration
    message, actions = chatbot.chat()
    # convert to html
    # message = message.replace('\n', '<br>')
    return render_template("index.html", text=message)


@app.route("/pivot")
def pivot_entity():
    facet = request.args.get('facet')
    entity = request.args.get('entity')
    action = (facet, entity)
    message, actions = chatbot.chat(action)
    # convert to html
    # message = message.replace('\n', '<br>')
    return message


@app.route("/continue")
def continue_exploration():
    message, actions = chatbot.chat()
    # convert to html
    # message = message.replace('\n', '<br>')
    return message


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8008)
