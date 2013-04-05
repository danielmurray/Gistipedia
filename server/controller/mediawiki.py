import requests
import re

class MediaWiki():
	url = 'http://en.wikipedia.org/w/api.php'

  	def __init__(self):
  		print('initialized')

  	def queryText(self, pageTitle):
  		wikimarkup = self.queryMarkup(pageTitle)
		norefs = re.sub('<ref[\S\s]*?</ref>', ' ', wikimarkup)
		nocomments = re.sub('<!--[\S\s]*?-->', ' ', norefs)
		body = nocomments.split("'''"+pageTitle+"'''")[1]
		nobottom = body.split("== See also ==")[0]
		notemplates = self.textParse('{{', '}}', nobottom)
		rawText = re.sub('[^\w\s]', '', notemplates)
		return rawText

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

	def textParse(self, openningTag, closingTag, s):
  		print('1')
		recursionCount = 0
		openingIndices = []
		closingIndices = []
		openingIndices.append(0)
		splitStrings = [] 
		s = s.encode('ascii', 'ignore')
		for i, c in enumerate(s):
			if c == openningTag[0]:
				for j, tag in enumerate(openningTag):
					# print openningTag, i+j, len(s)
					if i+j > len(s):
						break
					if tag == s[i+j]:
						openfound = 1
					else:
						openfound = 0
						break
				if openfound == 1:
					# print 'found open', i, recursionCount
					if recursionCount <= 0:
						closingIndices.append(i)
					recursionCount += 1
			if c == closingTag[0]:
				for j, tag in enumerate(closingTag):
					# print closingTag, i+j, len(s)
					if i+j > len(s)-1:
						break
					if tag == s[i+j]:
						closefound = 1
					else:
						closefound = 0
						break
				if closefound == 1:
					# print 'found close', i, recursionCount
					if recursionCount == 1:
						openingIndices.append(i+len(closingTag)+1)
						recursionCount -= 1
					elif recursionCount <= 0:
						openingIndices[-1] = i+len(closingTag)+1
					else:
						recursionCount -= 1
		closingIndices.append(len(s))
		# print len(openingIndices)
		# print len(closingIndices)
		for i,openTag in enumerate(openingIndices):
			splitStrings.append(s[openTag:closingIndices[i]])
		returnString = ''
		for i,text in enumerate(splitStrings):
			returnString += text + ' '
		return returnString