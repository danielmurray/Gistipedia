from __future__ import with_statement
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack
import json
import socketio
import hashlib
import controller
from gevent import monkey; monkey.patch_all()
import gevent

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

wikipedia = controller.MediaWiki()

@app.route('/')
def init():
    message = 'Enter Query'
    return render_template('test.html', message=message)

@app.route('/query/', methods=['GET'])
def search():
    query = request.args.get('query');
    wikicontent = wikipedia.findArticles(query)
    return json.dumps(wikicontent)

@app.route('/<pageTitle>')
def content(pageTitle):
    wikicontent = wikipedia.fetchText(pageTitle)
    return render_template('wikidump.html', wikicontent=wikicontent)


if __name__ == '__main__':
    app.run()