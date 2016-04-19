from glob import glob
import json
import pandas
import numpy
import pickle
import os

home = os.environ["HOME"]
base = "%s/data/pubmed" %os.environ["LAB"]
outfolder = "%s/methods" %(base)
repo_folder = "%s/repos" %(base)
scripts = "%s/SCRIPT/python/repofish/analysis/methods" %(home)

if not os.path.exists(outfolder):
    os.mkdir(outfolder)

files = glob("%s/*.json" %repo_folder)

jobfile = "%s/parsereopos.job" %(scripts)
filey = open(jobfile,'w')

# Take a look at repo urls to help parsing
urls = []
pmids = []
for f in files:
    print "Adding %s to list" %(f)
    result = json.load(open(f,'r'))
    pubmed_paper = str(result["pmid"])
    urls = urls + result["github"]
    pmids = pmids + [pubmed_paper] * len(result["github"])

# How many?
len(numpy.unique(pmids))
# 4240
len(urls)
# 6135

# Save to inputs file
inputs = dict()
inputs["urls"] = urls
inputs["pmids"] = pmids
pickle.dump(inputs,open("%s/inputs.pkl" %outfolder,"wb"))

seen = []
for f in files:
    result = json.load(open(f,'r'))
    pubmed_paper = result["pmid"]
    for repo_url in result["github"]:        
        if repo_url not in seen:
            print "Parsing %s" %(repo_url)
            seen.append(repo_url)
            repo_name = repo_url.split("/")[-1]
            user_name = repo_url.split("/")[-2]
            output_file = "%s/%s_%s_functions.tsv" %(outfolder,user_name,repo_name)
            if not os.path.exists(output_file):
                filey.writelines("python parse_imports.py %s %s %s" %(repo_url, output_file, pubmed_paper))
           
filey.close()
