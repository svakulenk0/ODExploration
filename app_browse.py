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

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route("/browse")
def home():
    chatbot.history = []
    chatbot.goal = []
    # start exploration
    message, actions = chatbot.chat(start=True)
    # convert to html
    # message = message.replace('\n', '<br>')
    return render_template("browse.html", text=str(message,'utf-8'))
    # return render_template("index.html")


@app.route("/get")
@app.route("/search_get")
def search():
    userText = request.args.get('msg')
    message, actions = chatbot.search(userText)
    # message, actions = chatbot.chat(keywords=userText)
    # convert to html
    # message = message.replace('\n', '<br>')
    return message


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


@app.route("/restart")
def restart():
    message, actions = chatbot.restart()
    return message



@app.route("/search")
def search_home():
    chatbot = DialogAgent(search_only=True)
    return render_template("search.html")



@app.route("/search_continue")
def continue_search():
    message, actions = chatbot.search()
    return message



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8008)
