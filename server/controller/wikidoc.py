from random import choice
import requests
import json
import re

backgroundModelFile = open('./controller/wikiOccurance.txt', 'r')
backgroundModel = {}
for line in backgroundModelFile:
	word = line.split(' ')[0]
	probability = line.split(' ')[1].split('\n')[0]
	backgroundModel[word] = probability

class WikiDoc():

  	def __init__(self, query):
  		self.url = 'http://en.wikipedia.org/w/api.php'
  		self.searchResults = self.findArticles(query)
  		#Best Match from wikipedia
		self.pageTitle = self.searchResults['query']['search'][0]['title']
		self.markup = self.queryMarkup(self.pageTitle)
  		self.textAndLinks, self.footer = self.preFormat(self.markup, self.pageTitle)

  		#Document General data
  		self.links, self.linkIndexDict, self.sentences = self.linksAndSentences(self.textAndLinks)
  		self.sortLinks = sorted(self.hashMap(self.links).iteritems(), key=lambda item: -item[1])
  		self.linkObjects = self.constructLinks(self.linkIndexDict, self.sortLinks, self.sentences)
  		self.text = self.rawText(self.textAndLinks)
  		self.categories = self.docCategories(self.footer)
  		self.languageModel = self.languageModel(self.text)
		
		#Image Acquisition
		self.images = self.imageURLS(self.pageTitle)
		self.randomImage = ''
		self.randomImageURL = ''
	  	if len(self.images) > 0:
	  		self.randomImage = choice(self.images)
	  		self.randomImageURL = self.randomImage['thumbBig']

	def jsonify(self):
		jsonGoodies = {
			'title': self.pageTitle,
			'text': self.text,
			'summary': self.sentences[:5],
			'languageModel': self.languageModel,
			'links': self.linkObjects,
			'categories': self.categories,
			'images': self.images,
			'randomImage': self.randomImage
		}
		return jsonGoodies

	def languageModel(self, text):
  		backgroundLanguageModel = backgroundModel
		words = re.split(' ', text)
		unigramLanguageModel = self.hashMap(words)
		#Creating a normalize language model of document words
		normalizedLanguageModel = self.normalLangModel(unigramLanguageModel,backgroundLanguageModel)
		return normalizedLanguageModel


	def hashMap(self, textArray):
		languageModel = {}
		for word in textArray:
			if word != '':
				if languageModel.get(word) != None:
					languageModel[word] += 1
				else:
					languageModel[word] = 1
		return languageModel

	def normalLangModel(self, unigram, background):

		backgroundCount = len(background)
		unigramCount = len(unigram)
		normalizedLanguageModel = {}
		for word in unigram:
			#if word in unigram does not exist, don't just divide by zero
			#else divide by the background word count + 1
			if background.get(word) == None:
				backProb = 1/float(backgroundCount + 2000)
			else:
				backProb = (int(background[word]) + 1)/float(backgroundCount + 2000)
			normalizedLanguageModel[word] = (unigram[word]/float(unigramCount))/float(backProb)
		return normalizedLanguageModel

	def topWords(self, normalizedLanguageModel):
		return sorted(normalizedLanguageModel.iteritems(), key=lambda item: -item[1])

  	def preFormat(self, text, pageTitle):
  		wikimarkup = text
   		wikimarkup, footer = self.articleBody(wikimarkup,pageTitle)
  		wikimarkup = self.removeCitationRefs(wikimarkup)
		wikimarkup = self.tagParse('{{', '}}', wikimarkup, 'delete')
		wikimarkup = self.removeCitationRefs(wikimarkup)		
		wikimarkup = self.removeComments(wikimarkup)
		wikimarkup = self.removeImages(wikimarkup)
		wikimarkup = re.sub('\\n','',wikimarkup)
		return (wikimarkup, footer)

	def linksAndSentences(self, text):
		links = []
  		linkIndices = {}
  		sentences = []
		sentenceArray = text.split('. ')
  		for sentenceIndex, sentence in enumerate(sentenceArray):
  			linksInSentence = re.findall('.*?\[\[(.*?)\]\].*?',sentence)
  			for i, link in enumerate(linksInSentence):
  				title = link.split('|')[0].lower()
  				linkIndices[title] = sentenceIndex
  				links.append(title)
  			sentence = re.sub('\[\[[^]]*?\|', '', sentence)
  			sentence = re.sub('==[\S\s]*?==', '', sentence)
  			sentence = re.sub('[\[\]\{\}]', '', sentence)
			sentence = re.sub('[^\w\s(\'\'),&]', ' ', sentence)
  			sentence += '. '
  			sentences.append(sentence)
  		return (links, linkIndices, sentences)

	def constructLinks(self, linkIndices, sortLinks, sentences):
		linkObjects = []
		for i, link in enumerate(sortLinks):
			linkObject = {}
			linkObject['title'] = link[0]
			linkObject['count'] = link[1]
			linkObject['sentences'] = sentences[linkIndices[link[0]]] 
			linkObjects.append(linkObject)
		return linkObjects

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
  		acceptableMimes = [
			'jpeg',
			'jpg',
			'png',
			'gif',
			'JPEG',
			'JPG',
			'PNG',
			'GIF'
		]
  		wikiImageMarkup = self.findImages(pageTitle)
  		if len(wikiImageMarkup) == 0:
  			return []
  		imageDicts = []
		for imageMarkup in wikiImageMarkup.itervalues():
			imageInfo = imageMarkup.get('imageinfo')
			if imageInfo == None or len(imageInfo) == 0:
				continue
			else:
				imageInfo = imageInfo[0]
				if any(x in imageInfo.get('mime') for x in acceptableMimes):
					imageDict = {}
					imageDict['file'] = imageMarkup['title']
					imageDict['title'] = imageDict['file'].split(':')[1]
					imageDict['height'] = imageInfo['height']
					imageDict['width'] = imageInfo['width']
					imageDict['size'] = imageInfo['size']
					imageDict['url'] = imageInfo['url']
					imageDict['thumbBig'] = imageInfo['thumburl']
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
		footer = ''
		referenceTags = [
			"==References==",
			"== References =="
		]
		for referenceTag in referenceTags:
			page = body.split(referenceTag)
			body = page[0]
			if len(page) > 1:
				footer = page[1]
		return (body,footer)

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
		]
		# for i, index in enumerate(openingIndices):
		# 	print index, closingIndices[i]
		while openIndexItr < len(openingIndices) and closeIndexItr < len(closingIndices):
			if openIndexItr+1 < len(openingIndices) and openingIndices[openIndexItr] < closingIndices[closeIndexItr]:
				#Opening Tag Found
				if depthCounter == 0:
					stringIndices.append([openingIndices[openIndexItr]-1,1])
				depthCounter += 1
				openIndexItr += 1
			else:
				#Closing Tag Found
				if depthCounter < 2:
					stringIndices.append([closingIndices[closeIndexItr]+len(closingTag),0])
				depthCounter -= 1
				closeIndexItr += 1
		stringIndices.append([len(text),1])
		finalStringIndices = []
		# for i, index in enumerate(stringIndices):
		# 	print index
		lastStringStart = 0
		for indexTuples in stringIndices:
			if indexTuples[1] == 0:
				finalStringIndices.append([indexTuples[0], None])
			else:
				if len(finalStringIndices) is 0: #If this is the firs topening tag put the string star before it
					finalStringIndices.append([0, None])
				finalStringIndices[-1][1] = indexTuples[0]
		# for i, index in enumerate(finalStringIndices):
		# 	print index
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

	
  	def backgroundLanguageModel(self):
  		#This is a pretty terrible background model, but it is alright for testing
  		#With the help of professor zhang hopefully we can get a better background model
  		wikipedia = ''
		wikipedia += WikiDoc('Life').jsonify()['text']
		wikipedia += WikiDoc('Philosophy').jsonify()['text']
		wikipedia += WikiDoc('Reality').jsonify()['text']
		wikipedia += WikiDoc('Language').jsonify()['text']
		wikipedia += WikiDoc('Art').jsonify()['text']
		wikipedia += WikiDoc('Europe').jsonify()['text']
		wikipedia += WikiDoc('Asia').jsonify()['text']
		wikipedia += WikiDoc('North America').jsonify()['text']
		wikipedia += WikiDoc('Science').jsonify()['text']
		wikipedia += WikiDoc('Math').jsonify()['text']
		wikipedia += WikiDoc('History').jsonify()['text']
		wikipedia += WikiDoc('Psychology').jsonify()['text']
		wikipedia += WikiDoc('Literature').jsonify()['text']
		wikipedia += WikiDoc('Africa').jsonify()['text']
		wikipedia += WikiDoc('Physics').jsonify()['text']
		wikipedia += WikiDoc('Chemistry').jsonify()['text']
		wikipedia += WikiDoc('Sociology').jsonify()['text']
		wikipedia += WikiDoc('Business').jsonify()['text']
		wikipedia += WikiDoc('Politics').jsonify()['text']
		wikipedia += WikiDoc('Engineering').jsonify()['text']
		wikipedia += WikiDoc('Biology').jsonify()['text']
		wikipedia += WikiDoc('Space').jsonify()['text']
		return wikipedia

  	def findImages(self, pageTitle):
	    """
	    Acquire Wikipage's Images witha list of URLs 
	    """
	    fileNames = []
	    queryparams = {
			"format": 'json',
			"action": 'query',
			"titles": pageTitle,
			"redirects": 'true',
			"generator": 'images',
			"gimlimit": 500,
			"prop": 'imageinfo',
			"iiprop": 'url|mime|size',
			"iiurlwidth": '500px'
		}
	    r = self.fetch(self.url, queryparams)
	    if not r.json():
	        #Oops no picture, oh well who cares
	        print 'No photo'
	        return[]
	    return r.json()['query']['pages']

	def createImageURL(self, fileTitle, width, height):
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
			"iiurlwidth": width,
			"iiurlheight": height,
		}
	    r = self.fetch(self.url, queryparams)
	    if not r.json:
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
	query = "Beijing"
	wikipedia = WikiDoc(query)
	# for link in wikipedia.sortLinks:
	# 	print link, wikipedia.linkIndexDict[link[0]]
	# 	print wikipedia.sentences[wikipedia.linkIndexDict[link[0]]]
	# for key,value in wikipedia.links.iteritems():
	# 	print key.encode('ascii', 'ignore'), value
	# for category in wikipedia.categories:
	# 	print category



