from random import choice
import json
from wikidoc import WikiDoc
import re
from numpy import *
from numpy.linalg import *
from numpy.random import *



class WikiGraph():

  	def __init__(self, query, doccount):
  		self.doccount = doccount
  		self.rootDoc = WikiDoc(query)
  		self.text  = self.rootDoc.text
  		self.links = self.rootDoc.links
  		self.wikiDocs = []
  		self.wikiDocs.append(self.rootDoc)


  	def addChileNode(self, query):
		pageTitle = self.rootDoc.findArticles(query)['query']['search'][0]['title']
  		images = self.rootDoc.imageURLS(pageTitle)
  		thumbImage = {
  			'thumbSmall': '',
  			'thumbBig': ''
  		}
	  	if len(images) > 0:
	  		randomImage = choice(images)
	  		thumbImage['thumb'] = randomImage
	  		thumbImage['thumbSmall'] = self.rootDoc.createImageURL( randomImage['file'], '250px', '250px')
	  	return thumbImage

  	def nodeVectors():
  		# self.similarityMatrix = self.linkSimilarityMatrix(self.wikiDocs)
  		# self.YVectors, self.eigenVectors = self.mds(self.similarityMatrix)
  		# print query
  		print 'hello world'

  	def jsonify(self):
		jsonGoodies = {
			'doc': self.rootDoc.jsonify()
		}
		return jsonGoodies

	def linkSimilarityMatrix(self,wikiDocs):
		languageModels = {}
		links = []
		for wikidoc in wikiDocs:
			languageModels[wikidoc.pageTitle] = self.findTopWords(wikidoc.text)
			links.append(wikidoc.pageTitle)
		similarityMatrix = {}
		for link1 in links:
			similarityMatrix[link1] = {}
			for link2 in links:
				if link2 is link1:
					similarityMatrix[link1][link2] = 1
				elif similarityMatrix.get(link2):
					similarityMatrix[link1][link2] = similarityMatrix[link2].get(link1)
				else:
					similarityMatrix[link1][link2] = self.computeSimilarity(languageModels[link1], languageModels[link2])*pow(10,5)
					# print str(similarityMatrix[link1][link2]) + "     " + link1 + "      " + link2
		return similarityMatrix

	def computeSimilarity(self, model_1, model_2):
		mu = 1
		prob_diff = 0
		flag = 1
		#check which dictionary has more words
		if (len(model_1) < len(model_2)):
			#iterate through all the keys in the shorter dictionary
			for key in model_1.keys():
				mod_2_val = 0
				if (model_2.get(key) == None):
					mod_2_val = 0
					flag = 0
				else:
					mod_2_val = model_2.get(key)
				if (flag):
					prob_diff = prob_diff + abs(mod_2_val - model_1.get(key))
				else:
					prob_diff = prob_diff + mu*abs(mod_2_val - model_1.get(key))
		else:
			#if the second dictionary has less words
			for key in model_2.keys():
				mod_1_val = 0
				if (model_1.get(key) == None):
					mod_1_val = 0
					flag = 0
				else:
					mod_1_val = model_1.get(key)
				if (flag):
					prob_diff = prob_diff + abs(mod_1_val - model_2.get(key))
				else:
					prob_diff = prob_diff + mu*abs(mod_1_val - model_2.get(key))
		score = 1/prob_diff
		score = score/(mu*abs(len(model_1)-len(model_2)))
		return score

	def mds(self, simMatrix):
	    """
	    Multidimensional Scaling - Given a matrix of interpoint distances,
	    find a set of low dimensional points that have similar interpoint
	    distances.
	    """
	    simMatrixArray = []
	    for link1 in simMatrix:
	    	simMatrixArrayRow = []
	    	for link2 in simMatrix:
	    		simMatrixArrayRow.append( 1/float(simMatrix[link1][link2]) )
	    	simMatrixArray.append(simMatrixArrayRow)
	    # print simMatrixArray
	    d = array(simMatrixArray)
	    (n,n) = d.shape
	    E = (-0.5 * d**2)
	    # Use mat to get column and row means to act as column and row means.
	    Er = mat(mean(E,1))
	    Es = mat(mean(E,0))
	    # From Principles of Multivariate Analysis: A User's Perspective (page 107).
	    F = array(E - transpose(Er) - Es + mean(E))
	    [U, S, V] = svd(F)
	    Y = U * sqrt(S)
	    return (Y[:,0:2], S)


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

		
if __name__ == '__main__':
	wikipedia = WikiGraph('China',25)
	wikipedia.addChileNode('people%27s%20liberation%20army')
	# for i in range (0,10):
	# 	print wikipedia.wikiDocs[i].pageTitle + "     " + str(wikipedia.YVectors[i])
	# for word in wikipedia.topWords:
	# 	print word
	# for link in wikipedia.sortLinks:
	# 	print link[0]




