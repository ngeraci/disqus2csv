# Calisphere Disqus to CSV

Transform an XML file [exported from Disqus](https://help.disqus.com/developer/comments-export) to CSV.

Currently, this is written specifically for working with Disqus comments from Calisphere. It needs some more untangling to be truly generalizable.

Requires: pandas, lxml

**disqus_to_csv.py** is the main function.
```
usage: disqus_to_csv.py [-h] path [output]

Disqus XML to CSV

positional arguments:
  path        path to Disqus XML file
  output      optional path to CSV output file. Default is to use basename of
              XML file with .csv extension

optional arguments:
  -h, --help  show this help message and exit

```

**comments_by_user.py** lets you get a CSV of comments by a particular user.
```
usage: comments_by_user.py [-h] path username outfile

Disqus XML to CSV, filtered on a single username

positional arguments:
  path        path to Disqus XML file
  username    username to filter on
  outfile     path to output file

optional arguments:
  -h, --help  show this help message and exit
```
