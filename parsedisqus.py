import re
from lxml import etree
import pandas as pd
import argparse
import sys

def main(args=None):
	parser = argparse.ArgumentParser(
		description='Disqus XML to CSV')
	parser.add_argument(
		'path', 
		nargs=1, 
		help='path to Disqus XML file',
		type=str)
	if args is None:
		args = parser.parse_args()

	disqus2csv(args.path[0])

def tagParse(tag):
	return tag[19].upper() + tag[20:]

def disqus2csv(infile):
	disqusXML = etree.parse(infile)
	disqusRoot = disqusXML.getroot()
	threads = {}
	posts = []
	# regular expression to match an ARK
	arkRE = re.compile(r'(ark:/\d{5}\/[^/|\s]*)')
	titleRE = re.compile(r'Image\s*\/\s(.*)')
	titleRE2 = re.compile(r'Calisphere:\s*(.*)')

	#gather thread elements in a dict with Thread ID as key
	for element in disqusRoot.iterchildren():
		if element.tag == '{http://disqus.com}thread':
			threadID = element.attrib['{http://disqus.com/disqus-internals}id']
			for child in element.getchildren():
				if child.tag == "{http://disqus.com}link":
					ark = arkRE.search(child.text).group(1)
				if child.tag == "{http://disqus.com}title":
					try:
						title = titleRE.search(child.text).group(1)
					except:
						title = titleRE2.search(child.text).group(1)

			threads[threadID] = [ark, title]

	#gather post elements in a list
	for element in disqusRoot.iterchildren():
		if element.tag == '{http://disqus.com}post':
			post = {}
			post['Post ID'] = element.attrib['{http://disqus.com/disqus-internals}id']
			for child in element.getchildren():
				if child.text is not '\n            ' and child.text is not None:
					if child.getchildren():
						for grandchild in child.getchildren():
							if grandchild.text is not None:
								fieldName = tagParse(grandchild.tag)
								post[fieldName] = grandchild.text
					else:
						fieldName = tagParse(child.tag)
						post[fieldName] = re.sub('<[^<]+?>', '', child.text) #strip <p> tags from "Message"
				elif child.tag == '{http://disqus.com}thread':
					post['Thread ID'] = child.attrib['{http://disqus.com/disqus-internals}id']
			posts.append(post)

	#match posts to threads on Thread ID
	for post in posts:
		post['ARK'] = threads[post['Thread ID']][0]
		post['Image Title'] = threads[post['Thread ID']][1]

	#convert to pandas dataframe, generate URL from ARK, set column order and labels
	rawDF = pd.DataFrame.from_dict(posts)
	urls = []
	for ark in rawDF['ARK']:
		urls.append('https://calisphere.org/item/' + ark)
	rawDF['URL'] = pd.Series(urls).values
	df = rawDF[['Image Title', 'URL', 'ARK', 'Message', 'Name', 'Username', 'Email', 'CreatedAt']]
	df = df.rename(index=str, columns = {'CreatedAt':'Comment Date', 'Message':'Comment'})

	outfile = infile.replace('.xml','.csv')
	df.to_csv(outfile, index=False)

# main() idiom
if __name__ == "__main__":
    sys.exit(main())