"""extract comments by single username
"""
import argparse
import pandas as pd
from parsedisqus import *

def main(args=None):
    """Parse command line args.
    """
    parser = argparse.ArgumentParser(
        description='Disqus XML to CSV, filtered by username')
    parser.add_argument(
        'path',
        nargs=1,
        help='path to Disqus XML file',
        type=str)
    parser.add_argument(
        'username',
        nargs=1,
        help='username to get comments from',
        type=str)
    parser.add_argument(
        'outfile',
        nargs=1,
        help='path to output file',
        type=str)

    # print help if no args given
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # parse
    if args is None:
        args = parser.parse_args()

    dataframe = disqus2df(args.path[0])
    subset_df = dataframe[dataframe['Username']==args.username[0]]
    subset_df.to_csv(args.outfile[0], index=False)

if __name__ == "__main__":
    main()



