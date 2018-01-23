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
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return str(chatbot.get_response(userText).encode('utf8'))


@app.route("/show")
def show_dataset():
    dataset_id = request.args.get('msg')
    return str(chatbot.show_dataset(dataset_id).encode('utf8'))


@app.route("/facets")
def show_facets():
    return str(chatbot.show_facets().encode('utf8'))


@app.route("/samples")
def show_samples():
    facet = request.args.get('facet')
    entity = request.args.get('entity')
    return str(chatbot.subset(facet, entity).encode('utf8'))

@app.route("/pivot")
def pivot_entity():
    facets_entities = json.loads(request.args.get('facets_entities'))
    return str(chatbot.pivot(facets_entities).encode('utf8'))


@app.route("/summary")
def summarize_items():
    return str(chatbot.summarize_items().encode('utf8'))


@app.route("/more")
def get_more():
    samples = chatbot.sample_nodes(size=10)
    if samples:
        return str(samples.encode('utf8'))
    else:
        return str(chatbot.get_response("").encode('utf8'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8008)
