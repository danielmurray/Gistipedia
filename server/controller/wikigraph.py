from random import choice
import json
from wikidoc import WikiDoc
import re
from numpy import *
from numpy.linalg import *
from numpy.random import *
from multiprocessing import Process, Manager
import time


class WikiGraph():

  	def __init__(self, query, doccount):
  		self.rootDoc = WikiDoc(query)
  		self.text  = self.rootDoc.text
  		self.links = self.rootDoc.links
  		self.doccount  = int(doccount) if int(doccount) < len(self.links) else len(self.links)
  		manager = Manager()
  		self.wikiDocs = manager.list() #this is essentially an array that can be touched in parallell processes
  		self.wikiDocsLock = manager.Lock()
  		self.vectorsReady = False

  	def addChildNode(self, query):
		pageTitle = self.rootDoc.findArticles(query)['query']['search'][0]['title']
  		images = self.rootDoc.imageURLS(pageTitle)
  		thumbImage = {
  			'thumbSmall': '',
  			'thumbBig': ''
  		}
	  	if len(images) > 0:
	  		randomImage = choice(images)
	  		thumbImage['thumb'] = randomImage
	  		thumbImage['thumbSmall'] = self.rootDoc.createImageURL( randomImage['file'], '300px', '300px')
	  	p = Process(target=self.initLinkDoc, args=(pageTitle,self.wikiDocs,self.wikiDocsLock))
	  	p.start()
	  	return thumbImage

  	def initLinkDoc(self, pageTitle, wikiDocs, lock):
		lock.acquire(True)
  		wikidoc = WikiDoc(pageTitle)
  		wikiDocs.append(wikidoc)
		lock.release()
  			
  	def computeVectors(self):
  		self.similarityMatrix = self.linkSimilarityMatrix(self.wikiDocs)
  		self.YVectors, self.eigenVectors = self.mds(self.similarityMatrix)
  		return self.YVectors.tolist()

  	def waitForVectors(self, timeout=30, period=0.25):
		mustend = time.time() + timeout
		while time.time() < mustend:
			if len(self.wikiDocs) >= self.doccount:
				return True
			time.sleep(period)
		return True

  	def jsonify(self):
		jsonGoodies = {
			'doc': self.rootDoc.jsonify()
		}
		return jsonGoodies

	def linkSimilarityMatrix(self,wikiDocs):
		languageModels = {}
		docs = {}
		links = []
		sortedScores = []
		for wikidoc in wikiDocs:
			languageModels[wikidoc.pageTitle] = wikidoc.languageModel
			docs[wikidoc.pageTitle] = wikidoc
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
					score = self.computeSimilarity(languageModels[link1], languageModels[link2])
					similarityMatrix[link1][link2] = score
					# print str(similarityMatrix[link1][link2]) + "     " + link1 + "      " + link2
		# 			sortedScores.append( (link1+'-'+link2, score) )
		# self.sortedScores = sorted(sortedScores, key=lambda item: -item[1])
		# for score in self.sortedScores:
		# 	print score[1], score[0]
		return similarityMatrix

	def computeSimilarity(self, model_1, model_2):
		mu = 2
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
		score = 1/(prob_diff+1)
		score = score/float(mu*(1+abs(len(model_1)-len(model_2))))
		score = math.log(score)
		return 1/score

	def mds(self, simMatrix):
	    """
	    Multidimensional Scaling - Given a matrix of interpoint distances,
	    find a set of low dimensional points that have similar interpoint
	    distances.
	    """
	    simMatrixArray = []
	    for doc1 in self.wikiDocs:
	    	link1 = doc1.pageTitle
	    	simMatrixArrayRow = []
	    	for doc2 in self.wikiDocs:
	    		link2 = doc2.pageTitle
	    		simMatrixArrayRow.append( float(simMatrix[link1][link2]) )				
	    	simMatrixArray.append(simMatrixArrayRow)
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
	for word in wikipedia.rootdoc.languageModel:
		print word[0], word[1]
	# for i in range (0,10):
	# 	print wikipedia.wikiDocs[i].pageTitle + "     " + str(wikipedia.YVectors[i])
	# for link in wikipedia.sortLinks:
	# 	print link[0]




