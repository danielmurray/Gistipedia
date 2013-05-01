import json
import operator
import re
		
if __name__ == '__main__':
	
	file = open('./wikicorpus.txt')
	data = file.read()
	file.close()
	data = data.lower()
	data = re.sub('[^\w\s\']', '', data)
	data = re.sub('\n', ' ', data)
	wordarray = re.split(' ', data)
	wordcount = len(wordarray)
	bigOlDict = {}
	for word in wordarray:
		if bigOlDict.get(word) is None:
			bigOlDict[word] = 1
		else:
			bigOlDict[word] += 1
  	# sortWords = sorted(bigOlDict.iteritems(), key=operator.itemgetter(1))
  	# languageModel = {}
  	# for word in reversed(sortWords):
  	# 	languageModel[word[0]] = float(word[1])/wordcount
  	for word, occurrence in bigOlDict.iteritems():
  		print word, occurrence

