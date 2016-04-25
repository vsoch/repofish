from glob import glob
import json
import pandas
import requests
import numpy
import pickle
import os
import re

home = os.environ["HOME"]
base = "%s/data/pubmed" %os.environ["LAB"]
outfolder = "%s/methods" %(base)
repo_folder = "%s/repos" %(base)
scripts = "%s/SCRIPT/repofish/analysis/methods" %(home)
counts_folder = "%s/counts" %(base)

if not os.path.exists(counts_folder):
    os.mkdir(counts_folder)

urls = pickle.load(open("%s/inputs_categorized.pkl" %outfolder,"rb"))["repos"]
len(urls)
#5570

jobfile = "%s/count_extensions.job" %(scripts)
filey = open(jobfile,"w")

for entry in urls:
    pmid = entry[0]
    url = entry[1]
    filey.writelines("python %s/5.count_extensions.py %s %s %s\n" %(scripts,pmid,url,counts_folder))

filey.close()
    
