import json
from wikidoc import WikiDoc
import re

class WikiGraph():

  	def __init__(self, query):
  		self.rootDoc = WikiDoc(query)
  		self.text  = self.rootDoc.text
  		self.links = self.rootDoc.links
  		self.wikiDocs = []
  		for i, link in enumerate(self.links):
			print i, link.encode('ascii','ignore')
			tempDoc = WikiDoc(link)
			self.wikiDocs.append(tempDoc)
			self.text += tempDoc.text


if __name__ == '__main__':
	wikipedia = WikiGraph('National Palace Museum')
	wikimarkup = re.sub('\\n','',wikipedia.text)
	words = re.split(' ', wikimarkup)
	backgroundCount = len(words)
	backgroundLanguagModel = {}
	for word in words:
		if word != '':
			if backgroundLanguagModel.get(word) != None:
				backgroundLanguagModel[word] += 1
			else:
				backgroundLanguagModel[word] = 1
	wikimarkup = re.sub('\\n','',wikipedia.rootDoc.text)
	words = re.split(' ', wikimarkup)
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
			backProb = 1/float(backgroundCount + 2000)
		else:
			backProb = (backgroundLanguagModel[word] + 1)/float(backgroundCount + 2000)
		normalizedLanguageModel[word] = (unigramLanguagModel[word]/float(unigramCount))/float(backProb)
	sortedLanguageModel = sorted(normalizedLanguageModel.iteritems(), key=lambda item: -item[1])
	for word in sortedLanguageModel:
		print word[0].encode('ascii','ignore') , word[1]
