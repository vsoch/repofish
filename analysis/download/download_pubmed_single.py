#!/usr/bin/env python2

# This script will download pubmed papers for a given start and end index in the current
# ftp manifest file
# Usage : download_pubmed_muhaha.py start end download_folder

import sys
import pandas
from repofish.pubmed import download_pubmed

# Get the start and end index of ids from the command line
pmid = sys.argv[1]
download_folder = sys.argv[2]
email = sys.argv[3]

# Download the articles!
download_pubmed([pmid],download_folder)
