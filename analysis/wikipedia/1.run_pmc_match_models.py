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
outfolder = "%s/methods" %base
folders = glob("%s/*" %articles_folder)

words_vectors = "%s/analysis/models/vectors/methods_word2vec.tsv" %scripts
methods_vectors = "%s/analysis/models/method_vectors.tsv" %scripts

if not os.path.exists(outfolder):
    os.mkdir(outfolder)

len(folders)
#6218

# We will write a command to process xml files in each folder
count = 0
folder_count = 0
for folder in folders:
    xmls = glob("%s/*.nxml" %article_folder)
    for xml_file in xmls:
        if count == 0:
            jobfile = "%s/.job/%s_match_methods.job" %(scripts,folder_count)
            filey = open(jobfile,"w")
        elif count == 1000:
            count=0
            filey.close()
            folder_count +=1
            jobfile = "%s/.job/%s_match_methods.job" %(scripts,folder_count)
            filey = open(jobfile,"w")

        filey.writelines("python %s/analysis/wikipedia/1.pmc_match_models.py %s %s %s\n" %(scripts,xml_file,outfolder,words_vectors,methods_vectors))
        count+=1
