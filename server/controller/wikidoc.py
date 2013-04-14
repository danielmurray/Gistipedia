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
  		self.textAndLinks = self.preFormat(self.markup, self.pageTitle)
  		self.links = self.docLinks(self.textAndLinks)
  		self.text = self.rawText(self.textAndLinks)

	def jsonify(self):
		jsonGoodies = {
			'title': self.pageTitle,
			'text': self.text,
			'links': self.links,
		}
		return jsonGoodies

  	def preFormat(self, text, pageTitle):
  		wikimarkup = text
   		wikimarkup = self.articleBody(wikimarkup,pageTitle)
		wikimarkup = self.tagParse('{{', '}}', wikimarkup, 'delete')
		wikimarkup = self.removeCitationRefs(wikimarkup)		
		wikimarkup = self.removeComments(wikimarkup)
		wikimarkup = self.removeImages(wikimarkup)
		return wikimarkup

	def docLinks(self, text):
  		wikimarkup = text
		#links = re.findall('\[\[[\S\s]*?\]\]',wikimarkup)
		links = re.findall('.*?\[\[(.*?)\]\].*?',wikimarkup)
		returnedLinks = []
		for i, link in enumerate(links):
			# links[i] = re.split('\|', link)[0]
			links[i] = link.split('|')[0]
  		return links

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
		page = text.split("'''"+pageTitle+"'''")
		body = page[-1]
		body = body.split("==See also==")[0]
		body = body.split("== See also ==")[0]
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
		#print openingIndices
		#print closingIndices
		openIndexItr = 0
		closeIndexItr = 0
		depthCounter = 0
		stringIndices = [
			[0,0]
		]
		#print stringIndices
		while openIndexItr < len(openingIndices) and closeIndexItr < len(closingIndices):
			#print openingIndices[openIndexItr], closingIndices[closeIndexItr]
			#print openIndexItr, closeIndexItr, depthCounter
			if openIndexItr+1 < len(openingIndices) and openingIndices[openIndexItr] < closingIndices[closeIndexItr]:
				if depthCounter == 0:
					stringIndices.append([openingIndices[openIndexItr]-1,1])
					#print 'appended',[openingIndices[openIndexItr]-1,1]
				depthCounter += 1
				openIndexItr += 1
			else:
				if depthCounter < 2:
					stringIndices.append([closingIndices[closeIndexItr]+len(closingTag),0])
					#print 'appended',[closingIndices[closeIndexItr]+2,0]
				depthCounter -= 1
				closeIndexItr += 1
		stringIndices.append([len(text),1])
		#print stringIndices
		finalStringIndices = []
		for indexTuples in stringIndices:
			if indexTuples[1] == 0:
				finalStringIndices.append([indexTuples[0], None])
			elif finalStringIndices > 0: #indexTuples[1] must equal 
				finalStringIndices[-1][1] = indexTuples[0]
		# print finalStringIndices
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
		"""
		return re.sub('[^\w\s]', ' ', text)

  	def findArticles(self, query):
	    """
	    Looks for the top ten articles that match the search
	    LOL, Wikipedia uses lucene, we ended up using it anyway!
	    """
	    searchparams = {
			"format": 'json',
			"action": 'query',
			"list": 'search',
			"srlimit": 10,
			"srsearch": query,
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
	wikimarkup = re.sub('\\n','',wikipedia)
	words = re.split(' ', wikimarkup)
	#words = WikiDoc('China').jsonify()['links']
	backgroundCount = len(words)
	backgroundLanguagModel = {}
	for word in words:
		if word != '':
			if backgroundLanguagModel.get(word) != None:
				backgroundLanguagModel[word] += 1
			else:
				backgroundLanguagModel[word] = 1
	print backgroundLanguagModel.get('Mao')
	wikipedia = WikiDoc('China')
	# print json.dumps(wikipedia.jsonify())
	wikimarkup = re.sub('\\n','',wikipedia.jsonify()['text'])
	words = re.split(' ', wikimarkup)
	# words = WikiDoc('The Great Leap Forward').jsonify()['links']
	unigramCount = len(words)
	unigramLanguagModel = {}
	for word in words:
		if word != '':
			if unigramLanguagModel.get(word) != None:
				unigramLanguagModel[word] += 1
			else:
				unigramLanguagModel[word] = 1
	normalizedLanguageModel = {}
	for word in unigramLanguagModel:
		if backgroundLanguagModel.get(word) == None:
			backProb = 1/float(backgroundCount + 20000)
		else:
			backProb = (backgroundLanguagModel[word] + 1)/float(backgroundCount + 20000)
		normalizedLanguageModel[word] = (unigramLanguagModel[word]/float(unigramCount))/float(backProb)
	sortedLanguageModel = sorted(normalizedLanguageModel.iteritems(), key=lambda item: -item[1])
	for word in sortedLanguageModel:
		print word[0].encode('ascii','ignore') , word[1]

