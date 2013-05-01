from __future__ import with_statement
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack
import json
import hashlib
import controller

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

@app.route('/')
def init():
    return render_template('index.html')

@app.route('/picoftheday/', methods=['GET'])
def backgroundImage():
    app.picOfTheDay = controller.PicOfTheDay()
    return json.dumps(app.picOfTheDay.jsonify())

@app.route('/doc/<query>', methods=['GET'])
def doc(query):
    wikiDoc = controller.WikiDoc(query)
    return json.dumps(wikiPage.jsonify())

@app.route('/graph/<query>', methods=['GET'])
def graph(query):
    wikiPage = controller.WikiGraph(query)
    return json.dumps(wikiPage.jsonify())

if __name__ == '__main__':
    app.run()