from random import choice
import requests
import json
import re

class WikiDoc():

  	def __init__(self, query):
  		self.url = 'http://en.wikipedia.org/w/api.php'
  		self.searchResults = self.findArticles(query)
  		#Best Match from wikipedia
		self.pageTitle = self.searchResults['query']['search'][0]['title']
		self.markup = self.queryMarkup(self.pageTitle)
  		#Footer is filled in articleBody, using this subset of text decreases runtime
		self.footer = ''
  		self.textAndLinks = self.preFormat(self.markup, self.pageTitle)
  		self.links = self.docLinks(self.textAndLinks)
  		self.text = self.rawText(self.textAndLinks)
  		self.categories = self.docCategories(self.footer)
  		self.images = self.imageURLS(self.pageTitle)
  		randomImage = choice(self.images)
  		# self.randomImageURL = self.createImageURL( randomImage['file'], randomImage['height'], randomImage['width']  )
  		self.randomImageURL = self.createImageURL( randomImage['file'], '400px')

	def jsonify(self):
		jsonGoodies = {
			'title': self.pageTitle,
			'text': self.text,
			'links': self.links,
			'categories': self.categories,
			'images': self.images,
			'randomImageURL': self.randomImageURL
		}
		return jsonGoodies

  	def preFormat(self, text, pageTitle):
  		wikimarkup = text
   		wikimarkup = self.articleBody(wikimarkup,pageTitle)
		wikimarkup = self.tagParse('{{', '}}', wikimarkup, 'delete')
		wikimarkup = self.removeCitationRefs(wikimarkup)		
		wikimarkup = self.removeComments(wikimarkup)
		wikimarkup = self.removeImages(wikimarkup)
		wikimarkup = re.sub('\\n','',wikimarkup)
		return wikimarkup

	def docLinks(self, text):
		if text == '':
			return []
  		wikimarkup = text
		links = re.findall('.*?\[\[(.*?)\]\].*?',wikimarkup)
		for i, link in enumerate(links):
			links[i] = link.split('|')[0].lower()
  		return links

  	def docCategories(self, text):
  		if text == '':
			return []
		#Text here should be the articles footer initialized in article body
  		wikimarkup = text
		categories = re.findall('.*?\[\[Category:(.*?)\]\].*?',wikimarkup)
		for i, category in enumerate(categories):
			categories[i] = category.split('|')[0].lower()
  		return categories

  	def imageURLS(self, pageTitle):
		wikiObject = self.findImages(pageTitle)
		acceptableMimes = [
			'jpeg',
			'png',
			'gif'
		]
		imageDicts= []
		for imageURL in wikiObject.iteritems():
			if imageURL[1].get('imageinfo'):
				imageinfo = imageURL[1]['imageinfo'][0]
				if any(x in imageinfo['mime'] for x in acceptableMimes):
					imageDict = {}
					imageDict['file'] = imageURL[1]['title']
					imageDict['title'] = imageDict['file'].split(':')[1]
					imageDict['height'] = imageinfo['height']
					imageDict['width'] = imageinfo['width']
					imageDict['size'] = imageinfo['size']
					imageDicts.append(imageDict)
		return imageDicts

	def removeCitationRefs(self, text):
		"""
		Templates are a rat's nest of content, external links
		and unneccesary content, this code exlcudes templates from
		the raw text of the document
		"""
		return re.sub('<ref[\S\s]*?</ref>', ' ', text)

	def removeComments(self, text):
		"""
		Sometimes Wiki authors will place comments in the markup
		as messages to the other authors. This removes those comments
		as they may not always be relevant to the document
		"""
		return re.sub('<!--[\S\s]*?-->', ' ', text)

	def articleBody(self, text, pageTitle):
		"""
		Splits the article into two parts, the authored text
		and the footer which holds external links and citations, this footer 
		also holds the page's categories, so we store this second part
		to self.footer to be used to acquire these categories later
		"""
		page = text.split("'''"+pageTitle+"'''")
		body = page[-1]
		referenceTags = [
			"==References==",
			"== References =="
		]
		for referenceTag in referenceTags:
			page = body.split(referenceTag)
			body = page[0]
			if len(page) > 1:
				self.footer = page[1]
		return body

	def tagParse(self, openingTag, closingTag, text, action):
		"""
		Templates our bookended by {{ }} and these elements
		may be nested, and RegEx sucks at parsing nested tags.
		This implementation isn't perfect but it accomplishes what we
		need here.
		"""
		openingIndices = [m.start() for m in re.finditer(openingTag, text)]
		closingIndices = [m.start() for m in re.finditer(closingTag, text)]
		openIndexItr = 0
		closeIndexItr = 0
		depthCounter = 0
		stringIndices = [
			[0,0]
		]
		while openIndexItr < len(openingIndices) and closeIndexItr < len(closingIndices):
			if openIndexItr+1 < len(openingIndices) and openingIndices[openIndexItr] < closingIndices[closeIndexItr]:
				if depthCounter == 0:
					stringIndices.append([openingIndices[openIndexItr]-1,1])
				depthCounter += 1
				openIndexItr += 1
			else:
				if depthCounter < 2:
					stringIndices.append([closingIndices[closeIndexItr]+len(closingTag),0])
				depthCounter -= 1
				closeIndexItr += 1
		stringIndices.append([len(text),1])
		finalStringIndices = []
		for indexTuples in stringIndices:
			if indexTuples[1] == 0:
				finalStringIndices.append([indexTuples[0], None])
			elif finalStringIndices > 0: #indexTuples[1] must equal 
				finalStringIndices[-1][1] = indexTuples[0]
		if action == 'content':
			return self.tagContent( text, finalStringIndices, openingTag, closingTag)
		else: 
			return self.removeTags( text, finalStringIndices)

	def tagContent(self, text, stringIndices, openingTag, closingTag):
		"""
		Returns content of the tags in an array
		"""
		tagContent = []
		for stringStartEnd in stringIndices:
			if stringStartEnd[1] == None:
				break
			tagContent.append( text[stringStartEnd[0]+len(openingTag)+1:stringStartEnd[1]-len(closingTag)-1])
		return tagContent

	def removeTags(self, text, stringIndices):
		"""
		Should only be called from the tagParse funciton, it is fed a wiki article
		and indices of the article to splice and create a new stringIndices
		Example...
		text = "Hello Wiki!"
		stringIndices = [
			[0,2],
			[4,8]
		]
		removeTags(text, stringIndices) will return 
		"Helo Wik"
		"""
		finalString = ''
		for stringStartEnd in stringIndices:
			finalString += text[stringStartEnd[0]:stringStartEnd[1]]
		return finalString


	def removeImages(self, text):
		"""
		Images our bookended like links [[ ]] but are prefaced with 
		"File:" and the contents of the string is nonsense
		"""
		text = re.sub('\[\[Image[\S\s]*?\]\]', ' ', text)
		return re.sub('\[\[File[\S\s]*?\]\]', ' ', text)

	def rawText(self, text):
		"""
		Only keeps the words, spaces, and digits in the file
		Also converts to lower case
		"""
		return re.sub('[^\w\s]', ' ', text).lower()

  	def findImages(self, pageTitle):
	    """
	    Acquire Wikipage's Images witha list of URLs 
	    """
	    queryparams = {
			"format": 'json',
			"action": 'query',
			"titles": pageTitle,

			"generator": 'images',
			"gimlimit": 500,
			"prop": 'imageinfo',
			"iiprop": 'mime|size'
		}
	    r = self.fetch(self.url, queryparams)
	    if not r.json():
	        raise SSMWError(r.text)
	    return r.json()['query']['pages']

	def createImageURL(self, fileTitle, width):
	    """
	    Returns the link in the Wikipedia commons to the 
	    image with the correct height and width
	    """
	    queryparams = {
			"format": 'json',
			"action": 'query',
			"titles": fileTitle,
			"prop": 'imageinfo',
			"iiprop": 'url',
			"iiurlwidth": width
		}
	    r = self.fetch(self.url, queryparams)
	    if not r.json():
	        raise SSMWError(r.text)
	    return r.json()['query']['pages'].itervalues().next()['imageinfo'][0]['thumburl']

  	def findArticles(self, query):
	    """
	    Looks for the top ten articles that match the search
	    LOL, Wikipedia uses lucene, we ended up using it anyway!
	    """
	    queryArray = query.split(' ')
	    newquery=''
	    for queryWord in queryArray:
	    	newquery += queryWord + '||'
	    searchparams = {
			"format": 'json',
			"action": 'query',
			"list": 'search',
			"srlimit": 10,
			"srsearch": newquery,
			"srprop": 'title|wordcount|snippet|url'
		}
	    r = self.fetch(self.url, searchparams)
	    if not r.json():
	        raise SSMWError(r.text)
	    return r.json()

  	def queryMarkup(self, pageTitle):
	    """
	    Acquire Wikipage by 
	    """
	    queryparams = {
			"format": 'json',
			"action": 'query',
			"titles": pageTitle,
			"prop": 'revisions',
			"rvprop": 'content'
		}
	    r = self.fetch(self.url, queryparams)
	    if not r.json():
	        raise SSMWError(r.text)
	    wikimarkup = r.json()['query']['pages'].itervalues().next()['revisions'][0]['*']
	    return wikimarkup

	def fetch(self, url, params=None):	
		r = requests.post(url, params=params)
		if not r.ok:
			#Here we should put more intense error handling, perhaps passing a message to the front end
			raise SSMWError(r.text)
		return r

if __name__ == '__main__':
	wikipedia = WikiDoc('Quiver Tree Forest Namibia')
	# for link in wikipedia.links:
	# 	print link
	# for category in wikipedia.categories:
	# 	print category



