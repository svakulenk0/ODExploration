'''
svakulenko
22 Dec 2017

Flas web app for chatbot interface based on https://github.com/chamkank/flask-chatterbot
'''

from flask import Flask, render_template, request

from dialog_agent import DialogAgent

app = Flask(__name__)

chatbot = DialogAgent()
# chatbot.chat(greeting="Welcome, I will show you around data.gv.at", simulate=False)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return str(chatbot.get_response(userText).encode('utf8'))


@app.route("/more")
def get_more_items():
    samples = chatbot.sample_items(size=10)
    if samples:
        return str(samples.encode('utf8'))
    else:
        return str(chatbot.get_response("").encode('utf8'))


if __name__ == "__main__":
    app.run(host="0.0.0.0")
