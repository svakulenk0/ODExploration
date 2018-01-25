'''
svakulenko
22 Dec 2017

Flas web app for chatbot interface based on https://github.com/chamkank/flask-chatterbot
'''
import json
from flask import Flask, render_template, request

from dialog_agent import DialogAgent

app = Flask(__name__)

chatbot = DialogAgent(search_only = True)


@app.route("/search")
def search_home():
    return render_template("search.html")


@app.route("/search_get")
def search():
    userText = request.args.get('msg')
    message, actions = chatbot.search(userText)
    # message, actions = chatbot.chat(keywords=userText)
    # convert to html
    # message = message.replace('\n', '<br>')
    return message


@app.route("/search_continue")
def continue_exploration():
    message, actions = chatbot.search()
    return message


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8008)
