#!/usr/bin/env python2

# This script will download pubmed papers for a given start and end index in the current
# ftp manifest file. We will use a local data frame and list of ids.

import sys
import pandas
import pickle
from brainbehavior.pubmed import download_pubmed

# Get the start and end index of ids from the command line
start = int(sys.argv[1])
end = int(sys.argv[2])
download_folder = sys.argv[3]
ftp_pickle = sys.argv[4]
ids_pickle = sys.argv[5]


# Get pubmed ids for articles in database
pc_ids = pickle.load(open(ids_pickle,"rb"))

# Load the ftp matrix
ftp = pandas.read_pickle(ftp_pickle)

# Filter down to indices that we want
pc_ids = pc_ids[start:end]

# Download the articles!
download_pubmed(pc_ids,download_folder,ftp)
