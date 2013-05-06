from random import choice
import requests
import json
import re
from wikidoc import WikiDoc


class PicOfTheDay():

  	def __init__(self):
  		self.url = 'http://commons.wikimedia.org/w/api.php'
  		# Picture of the Day Implementation
  		# self.file = self.potdFileName()
  		# self.caption = self.potdCaption()
  		# self.url = self.fileURL(self.file, '1310px')
  		# self.title = self.findTitle(self.caption)
  		# Random Wikipedia Picture Implementation
  		self.file = self.randomFileName()
  		self.url = self.fileURL(self.file, '1310px')
  		self.query = self.filenameToQuery(self.file)
  		self.doc = WikiDoc(self.query)

  	def jsonify(self):
  		return {
  			'title': self.doc.pageTitle,
  			'file': self.file,
  			'url': self.url,
  		}

  	def randomFileName(self):
	    """
	    Acquires the name of random wikipedia file
	    """
	    queryparams = {
			"format": 'json',
			"action": 'query',
			"list": 'random',
			"rnnamespace": 6,
			"rnlimit": 1
		}
	    r = self.fetch(self.url, queryparams)
	    if not r.json():
	        raise SSMWError(r.text)
	    return r.json()['query']['random'][0]['title'].split(':')[1]

  	def potdFileName(self):
	    """
	    Acquires the name of wikipedia's pic of the day
	    """
	    queryparams = {
			"format": 'json',
			"action": 'expandtemplates',
			"text": '{{Potd/{{CURRENTYEAR}}-{{CURRENTMONTH}}-{{CURRENTDAY2}}}}'
		}
	    r = self.fetch(self.url, queryparams)
	    if not r.json():
	        raise SSMWError(r.text)
	    return r.json()['expandtemplates']['*']

	def potdCaption(self):
	    """
	    Acquires the name of wikipedia's pic of the day
	    """
	    queryparams = {
			"format": 'json',
			"action": 'expandtemplates',
			"text": '{{Potd/{{CURRENTYEAR}}-{{CURRENTMONTH}}-{{CURRENTDAY2}} (en)}}'
		}
	    r = self.fetch(self.url, queryparams)
	    if not r.json():
	        raise SSMWError(r.text)
	    return r.json()['expandtemplates']['*']

	def fileURL(self, fileName, width):
	    """
	    Acquires the url of a given image
	    """
	    queryparams = {
			"format": 'json',
			"action": 'query',
			"titles": 'File:'+fileName,
			"prop": 'imageinfo',
			"iiprop": 'url',
			"iiurlwidth": width
		}
	    r = self.fetch(self.url, queryparams)
	    if not r.json():
	        raise SSMWError(r.text)
	    return r.json()['query']['pages'].itervalues().next()['imageinfo'][0]['thumburl']

	def fetch(self, url, params=None):	
		r = requests.post(url, params=params)
		if not r.ok:
			#Here we should put more intense error handling, perhaps passing a message to the front end
			raise SSMWError(r.text)
		return r

	def findTitle(self, caption):
		titles = re.findall('.*?\[\[(.*?)\]\].*?',caption)
		concatenatedTitles = []
		for title in titles:
			concatenatedTitles.append(title.split('|')[-1])
		return concatenatedTitles[0]

	def filenameToQuery(self, fileName):
		fileName = fileName.split('.')[0]
		fileName = re.sub('\P{L}+', ' ', fileName)
		fileName = fileName.split(' ')[:2]
		query = '||'.join(fileName)
		return query

if __name__ == '__main__':
	picoftheday = PicOfTheDay()
