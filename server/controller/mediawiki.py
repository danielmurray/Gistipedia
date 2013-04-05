import requests
import json
import re

class MediaWiki():
	url = 'http://en.wikipedia.org/w/api.php'

  	def __init__(self):
		x=0
		#print('initialized')

  	def fetchDocData(self, pageTitle):
  		wikimarkup = self.queryMarkup(pageTitle)
  		return self.docData(wikimarkup, pageTitle, 'all')

  	def fetchText(self, pageTitle):
  		wikimarkup = self.queryMarkup(pageTitle)
  		return self.docData(wikimarkup, pageTitle, 'text')

  	def fetchLinks(self, pageTitle):
  		wikimarkup = self.queryMarkup(pageTitle)
  		return self.docData(wikimarkup, pageTitle, 'links')

  	def docData(self, text, pageTitle, desriredContent):
  		wikimarkup = text
   		wikimarkup = self.articleBody(wikimarkup,pageTitle)
		wikimarkup = self.tagParse('{{', '}}', wikimarkup, 'delete')
		wikimarkup = self.removeCitationRefs(wikimarkup)		
		wikimarkup = self.removeComments(wikimarkup)
		wikimarkup = self.removeImages(wikimarkup)
		if desriredContent == 'links':
			links = self.docLinks(wikimarkup)
			return links
		elif desriredContent == 'text':
			wikimarkup = self.rawText(wikimarkup)
  			return wikimarkup
  		else:
  			doc = []
  			doc['links'] = self.docLinks(wikimarkup)
  			doc['text'] = self.rawText(wikimarkup)
			return doc

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
			"srsearch": str(query),
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
			raise SSMWError(r.text)
		return r

if __name__ == '__main__':
	wikipedia = MediaWiki()
	pageTitle = 'China'
	wikimarkup = wikipedia.fetchDocData(pageTitle)
	print json.dumps(wikimarkup)