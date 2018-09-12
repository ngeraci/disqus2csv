""" Command-line tool to convert Disqus comments export (custom XML format) to CSV.
More info on Disqus XML format: https://help.disqus.com/developer/custom-xml-import-format
"""
import re
import argparse
import pandas as pd
from lxml import etree

def main(args=None):
    """Parse command line args.
    """
    parser = argparse.ArgumentParser(
        description='Disqus XML to CSV')
    parser.add_argument(
        'path',
        nargs=1,
        help='path to Disqus XML file',
        type=str)
    if args is None:
        args = parser.parse_args()

    # print help if no args given
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # parse
    if args is None:
        args = parser.parse_args()

    dataframe = disqus2df(args.path[0])

    write_out(dataframe, args.path[0])

def disqus2df(infile):
    """Parse XML, match individual posts to thread info, return pandas dataframe.
    """
    disqus_xml = etree.parse(infile)
    disqus_root = disqus_xml.getroot()

    threads = get_threads(disqus_root)
    posts = get_posts(disqus_root)
    posts = match_threads_posts(threads, posts)
    dataframe = to_dataframe(posts)

    return dataframe

def get_threads(disqus_root):
    """Return dict of thread elements with Thread ID as key
    """
    threads = {}

    ark_re = re.compile(r'(ark:/\d{5}\/[^/|\s]*)')
    title_re = re.compile(r'Image\s*\/\s(.*)', flags=re.DOTALL)
    title_re2 = re.compile(r'Calisphere:\s*(.*)', flags=re.DOTALL)

    for element in disqus_root.findall('{http://disqus.com}thread'):
        if element.tag == '{http://disqus.com}thread':
            thread_id = element.attrib['{http://disqus.com/disqus-internals}id']
            for child in element.getchildren():
                if child.tag == "{http://disqus.com}link":
                    ark = ark_re.search(child.text).group(1)
                if child.tag == "{http://disqus.com}title":
                    try:
                        title = title_re.search(child.text).group(1)
                    except AttributeError:
                        title = title_re2.search(child.text).group(1)
                    # collapse multiple whitespace
                    title = ' '.join(title.split())

            threads[thread_id] = [ark, title]

    return threads

def get_posts(disqus_root):
    """Return list of post elements.
    """
    posts = []
    for element in disqus_root.findall('{http://disqus.com}post'):
        post = {'Post ID': element.attrib['{http://disqus.com/disqus-internals}id']}

        for child in element.getchildren():
            if child.text and child.text.strip() != '\n':
                if child.getchildren():
                    for grandchild in child.getchildren():
                        if grandchild.text is not None:
                            field_name = tag_to_fieldname(grandchild.tag)
                            post[field_name] = grandchild.text
                else:
                    field_name = tag_to_fieldname(child.tag)
                    #strip <p> tags from "Message"
                    post[field_name] = re.sub('<[^<]+?>', '', child.text)
            elif child.tag == '{http://disqus.com}thread':
                post['Thread ID'] = child.attrib['{http://disqus.com/disqus-internals}id']
        posts.append(post)

    return posts

def match_threads_posts(threads, posts):
    """Match posts to threads on Thread ID. Return updated posts list.
    """
    for post in posts:
        post['ARK'] = threads[post['Thread ID']][0]
        post['Image Title'] = threads[post['Thread ID']][1]

    return posts

def to_dataframe(posts):
    """Convert to pandas dataframe, generate URL from ARK, set column order and labels.
    Return dataframe.
    """
    raw_dataframe = pd.DataFrame.from_dict(posts)
    urls = []
    for ark in raw_dataframe['ARK']:
        urls.append('https://calisphere.org/item/' + ark)
    raw_dataframe['URL'] = pd.Series(urls).values
    try:
        dataframe = raw_dataframe[['Name', 'Username', 'Email', 'CreatedAt',  'Message',
                                   'Image Title', 'URL', 'ARK']]
    except KeyError:
        # "email" not in export schema as of 2018-09
        dataframe = raw_dataframe[['Name', 'Username', 'CreatedAt', 'Message',
                                   'Image Title', 'URL', 'ARK']]

    dataframe = dataframe.rename(index=str,
                                 columns={'CreatedAt':'Comment Date', 'Message':'Comment'})

    return dataframe

def write_out(dataframe, infile):
    """write dataframe to csv.
    """
    outfile = infile.replace('.xml', '.csv')
    dataframe.to_csv(outfile, index=False)

def tag_to_fieldname(tag):
    """Get CSV fieldname from XML tag.
    """
    return tag[19].upper() + tag[20:]

if __name__ == "__main__":
    main()
