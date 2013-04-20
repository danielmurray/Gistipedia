import json
from wikidoc import WikiDoc
import re

class WikiGraph():

  	def __init__(self, query):
  		self.rootDoc = WikiDoc(query)
  		self.text  = self.rootDoc.text
  		self.links = self.rootDoc.links
  		# self.wikiDocs = []
  		# self.topWords = self.findTopWords(query) #Soon we may add the option to pass a variable
  		# self.topLinks = self.findTopLinks(query, self.topWords)
  		self.sortLinks = self.languageModel(self.links)
  		self.sortLinks = sorted(self.sortLinks.iteritems(), key=lambda item: -item[1])

  	def jsonify(self):
		jsonGoodies = {
			'doc': self.rootDoc.jsonify(),
			'links': self.sortLinks
		}
		return jsonGoodies

  	def findTopWords(self, query):
  		#Creating a hash map for background language model
  		backgroundText = self.backgroundLanguageModel()
  		words = re.split(' ', backgroundText)
		backgroundLanguageModel = self.languageModel(words)
		#Creating a hash map for the query language model
		words = re.split(' ', self.text)
		unigramLanguageModel = self.languageModel(words)
		#Creating a normalize language model of document words
		normalizedLanguageModel = self.sortNormalLangModel(unigramLanguageModel,backgroundLanguageModel)
		return normalizedLanguageModel
	
	def findTopLinks(self, query, topWordsModel):
		#Takes in a top word count and then 
		#finds the corresponding links to those 
		#top words	
		topWordsToLinks = []
		for wordTuple in topWordsModel:
			word = wordTuple[0]
			if word != query.lower():
				wordLinks = {}
				for link in self.links:
					linkArray = re.split(' ', link)
					matchfound = False
					for linkword in linkArray:
						if word == linkword:
							# print word.encode('ascii','ignore'), link.encode('ascii','ignore')
							matchfound = True
					if matchfound:
						if word == link:
							topWordsToLinks.append(link)
							break
						else:
							self.hashMapAdd(wordLinks, link)
				sortedWordLinks = sorted(wordLinks.iteritems(), key=lambda item: -item[1])
				if len(sortedWordLinks) > 0:
					if sortedWordLinks[0][1] > 1:
						topWordsToLinks.append(sortedWordLinks[0][0])
					else:
						for wordLink in sortedWordLinks:
							topWordsToLinks.append(wordLink[0])
			if len(topWordsToLinks) > 24:
				break
		return topWordsToLinks


	
	def hashMapAdd(self, hashmap, term):
		if term != '':
			if hashmap.get(term) != None:
				hashmap[term] += 1
			else:
				hashmap[term] = 1

	def languageModel(self, textArray):
		languageModel = {}
		for word in textArray:
			if word != '':
				if languageModel.get(word) != None:
					languageModel[word] += 1
				else:
					languageModel[word] = 1
		return languageModel

	def sortNormalLangModel(self, unigram, background):
		backgroundCount = len(background)
		unigramCount = len(unigram)
		normalizedLanguageModel = {}
		for word in unigram:
			#if word in unigram does not exist, don't just divide by zero
			#else divide by the background word count + 1
			if background.get(word) == None:
				backProb = 1/float(backgroundCount + 20000)
			else:
				backProb = (background[word] + 1)/float(backgroundCount + 20000)
			normalizedLanguageModel[word] = (unigram[word]/float(unigramCount))/float(backProb)
		sortedNormalLanguageModel = sorted(normalizedLanguageModel.iteritems(), key=lambda item: -item[1])
		return sortedNormalLanguageModel

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

		
if __name__ == '__main__':
	wikipedia = WikiGraph('Peking University')
	# for link in wikipedia.links:
	# 	print link.encode('ascii','ignore')
	for word in wikipedia.topWords:
	 	print word[0].encode('ascii','ignore'), word[1]
	# for word in wikipedia.topLinks:
	#  	print word.encode('ascii','ignore')
	# for link in wikipedia.sortLinks:
	# 	print link[0].encode('ascii','ignore'), link[1]


