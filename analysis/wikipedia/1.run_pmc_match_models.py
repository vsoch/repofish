from glob import glob
import json
import pandas
import requests
import numpy
import pickle
import os
import re

home = os.environ["HOME"]
scripts = "%s/SCRIPT/repofish" %home
base = "%s/data/pubmed" %os.environ["LAB"]
articles_folder = "%s/articles" %base
outfolder = "%s/methods_match" %base
folders = glob("%s/*" %articles_folder)

words_vectors = "%s/analysis/models/vectors/methods_word2vec.tsv" %scripts
methods_vectors = "%s/analysis/models/method_vectors.tsv" %scripts

if not os.path.exists(outfolder):
    os.mkdir(outfolder)

len(folders)
#6218

count = 0
for folder in folders:
    print "Parsing %s" %(folder)
    xmls = glob("%s/*.nxml" %folder)
    count = count + len(xmls)

count
#1248536

# We will write a command to process xml files in each folder
count = 0
folder_count = 0
for folder in folders:
    xmls = glob("%s/*.nxml" %folder)
    for xml_file in xmls:
        if count == 0:
            jobfile = "%s/analysis/wikipedia/.job/%s_match_methods.job" %(scripts,folder_count)
            filey = open(jobfile,"w")
        elif count == 4000:
            count=0
            filey.close()
            folder_count +=1
            jobfile = "%s/analysis/wikipedia/.job/%s_match_methods.job" %(scripts,folder_count)
            filey = open(jobfile,"w")
        filey.writelines('python %s/analysis/wikipedia/1.pmc_match_models.py "%s" %s %s %s\n' %(scripts,xml_file,outfolder,words_vectors,methods_vectors))
        count+=1

filey.close()

# Let's ask for 40 nodes, assuming we have 4000 jobs per launch, this means we want 100 jobs per core, with 15 minutes per command, this is 1500 minutes or 25 hours

# Now submit jobs to launch, we can only do 50 at a time

jobfiles = glob("%s/analysis/wikipedia/.job/*.job" %scripts)
for jobfile in jobfiles:
    os.system('launch -s %s -N 40 --runtime=26:00:00' %jobfile)
