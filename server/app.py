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
app.debug = True
app.wikiRequests = {}

@app.route('/')
def init():
    return render_template('index.html')

@app.route('/picoftheday/', methods=['GET'])
def backgroundImage():
    app.picOfTheDay = controller.PicOfTheDay()
    return json.dumps(app.picOfTheDay.jsonify())

@app.route('/root/', methods=['GET'])
def graph():
    query =  request.args['query']
    doccount =  request.args['doccount']
    wikiPage = controller.WikiGraph(query, doccount)
    app.wikiRequests[wikiPage.jsonify()['doc']['title']] = wikiPage
    return json.dumps(wikiPage.jsonify())

@app.route('/node/', methods=['GET'])
def node():
    root =  request.args['root']
    node =  request.args['node']
    graph = app.wikiRequests.get(root)
    nodeDoc = graph.addChileNode(node)
    return json.dumps(nodeDoc)

if __name__ == '__main__':
    app.run()
    # graph = graph('China', 25)
    # thing = node('China', 'shanghai')
    # thing = node('China', 'nanjing')
    # print app.wikiRequests['China'].wikiDocs[1].pageTitle