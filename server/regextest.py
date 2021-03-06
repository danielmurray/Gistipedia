import requests
import re
import json

url = 'http://en.wikipedia.org/w/api.php'

def textParse(openningTag, closingTag, action, s):
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

def findArticles(query):
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
    r = fetch(self.url, searchparams)
    if not r.json():
        raise SSMWError(r.text)
    return r.json()

def findLinks(self, s):
	linksWithMarkup = re.findall('\[\[[\S\s]*?\]\]',s)
	return linksWithMarkup[2:-2]

def queryMarkup(pageTitle):
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
    r = fetch(url, queryparams)
    if not r.json():
        raise SSMWError(r.text)
    wikimarkup = r.json()['query']['pages'].itervalues().next()['revisions'][0]['*']
    return wikimarkup

def fetch(url, params=None):	
	r = requests.post(url, params=params)
	if not r.ok:
		raise SSMWError(r.text)
	return r

def fetchRawText(self, pageTitle):
  		wikimarkup = self.queryMarkup(pageTitle)
  		return self.markupToRawText(wikimarkup, pageTitle)

def docData(self, text, pageTitle):
	wikimarkup = text
	wikimarkup = self.removeCitationRefs(text)		
	wikimarkup = self.removeComments(wikimarkup)
	wikimarkup = self.articleBody(wikimarkup,pageTitle)
	wikimarkup = self.removeTemplates(wikimarkup)
	
	wikimarkup = self.rawText(wikimarkup)
	return wikimarkup

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

def removeTemplates(self, text):
	"""
	Templates our bookended by {{ }} and these elements
	may be nested, and RegEx sucks at parsing nested tags.
	This implementation isn't perfect but it accomplishes what we
	need here.
	"""
	return re.sub('{{[\S\s]*?}}', ' ', text)

def rawText(self, text):
	"""
	Only keeps the words, spaces, and digits in the file
	"""
	return re.sub('[^\w\s]', ' ', text)
		
if __name__ == '__main__':
	pageTitle = 'Taiwan'
	wikimarkup = queryMarkup(pageTitle)
	norefs = re.sub('<ref[\S\s]*?</ref>', ' ', wikimarkup)
	nocomments = re.sub('<!--[\S\s]*?-->', ' ', norefs)
	body = nocomments.split("'''"+pageTitle+"'''")[1]
	nobottom = body.split("== See also ==")[0]
	notemplates = textParse('{{', '}}', 'remove', nobottom)
	rawText = re.sub('[^\w\s]', '', notemplates)
	print json.dumps(rawText)
