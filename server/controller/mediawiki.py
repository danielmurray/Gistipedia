import requests

class MediaWiki():
	url = 'http://en.wikipedia.org/w/api.php'

  	def __init__(self):
  		print('initialized')

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

  	def queryText(self, pageTitle):
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
	    print(r.json())
	    if not r.json():
	        raise SSMWError(r.text)
	    return r.json()

	def fetch(self, url, params=None):
		print('fetch')		
		r = requests.post(url, params=params)
		if not r.ok:
			raise SSMWError(r.text)
		return r