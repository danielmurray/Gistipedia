from __future__ import with_statement
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack
import json
import hashlib
import controller
import time

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
def root():
    query =  request.args['query']
    doccount =  request.args['doccount']
    wikiPage = controller.WikiGraph(query, doccount)
    app.wikiRequests[wikiPage.jsonify()['doc']['title'].lower()] = wikiPage
    return json.dumps(wikiPage.jsonify())

@app.route('/node/', methods=['GET'])
def node():
    root =  request.args['root'].lower()
    node =  request.args['node'].lower()
    graph = app.wikiRequests.get(root)
    nodeDoc = graph.addChildNode(node)
    return json.dumps(nodeDoc)

@app.route('/vectors/', methods=['GET'])
def vectors():
    root =  request.args['root'].lower()
    graph = app.wikiRequests.get(root)
    if graph.waitForVectors():
        vectors = graph.computeVectors()
        return json.dumps(vectors)
    else:
        return []

if __name__ == '__main__':
    app.run()
    # graph = graph('China', 25)
    # thing = node('China', 'shanghai')
    # thing = node('China', 'nanjing')
    # print app.wikiRequests['China'].wikiDocs[1].pageTitle