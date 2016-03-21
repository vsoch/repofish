#!/usr/bin/env python2

# This script will download pubmed papers for a given start and end index in the current
# ftp manifest file
# Usage : download_pubmed_muhaha.py start end download_folder ftp_pickle ids_pickle

from repofish.pubmed import download_pubmed
import sys
import pandas
import pickle

# Get the start and end index of ids from the command line
start = int(sys.argv[1])
end = int(sys.argv[2])
download_folder = sys.argv[3]
ftp_pickle = sys.argv[4]
ids_pickle = sys.argv[5]

pc_ids = pickle.load(open(ids_pickle,"rb"))
ftp = pickle.load(open(ftp_pickle,"rb"))

# Filter down to indices that we want
pmids = pc_ids[start:end]

# Download the articles!
download_pubmed(pmids,ftp,download_folder)
