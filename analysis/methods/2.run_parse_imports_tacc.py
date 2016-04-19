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
scripts = "%s/SCRIPT/python/repofish/analysis/methods" %(home)

if not os.path.exists(outfolder):
    os.mkdir(outfolder)

files = glob("%s/*.json" %repo_folder)


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

# inputs = pickle.load(open("%s/inputs.pkl" %outfolder,"rb"))

# Zip together
inputs = zip(inputs["pmids"],inputs["urls"])

# Remove links that are just to github
inputs = [x for x in inputs if not re.search("[http|https]://github.com$",x[1])]
inputs = [x for x in inputs if not re.search("[http|https]://www.github.com$",x[1])]

# Find urls that don't match pattern github.com/user/repo
needs_curation = [x for x in inputs if not re.search("[http|https]://(www.)?github.com/.*/.*$",x[1])]
inputs = [x for x in inputs if re.search("[http|https]://(www.)?github.com/.*/.*$",x[1])]

# We will need to parse links based on type
raw_files = []
gists = []
github_io = []
github_io_master = []
rest = []
nbviewer = []
users = []
manual_curation = []
github_help = []

while len(needs_curation) > 0:
    element = needs_curation.pop()
    # We've found a gist
    if re.search("[http|https]://gist.github.com/.*$",element[1]):
    #    print "GIST: %s" %element[1]
        gists.append(element)
    # Github help
    elif re.search("[http|https]://help.github.com/.*$",element[1]):
        github_help.append(element)
    # Github user main pages
    elif re.search("[http|https]://github.com/.*$",element[1]):
        users.append(element)
    # nbviewer
    elif re.search("nbviewer",element[1]):
        nbviewer.append(element)
    # We've found a raw file
    elif re.search("[http|https]://raw.github.com/.*$",element[1]):
    #    print "RAW: %s" %element[1]
        raw_files.append(element)
    # github io address associated with repo
    elif re.search("[http|https]://.*[.]github.io/.*$",element[1]):
        github_io.append(element)
    elif re.search("[http|https]://.*[.]github.com/.*$",element[1]):
        github_io.append(element)
    # github io address for entire association
    elif re.search("[http|https]://.*[.]github.io$",element[1]):
        github_io_master.append(element)
    elif re.search("[http|https]://.*[.]github.com$",element[1]):
        github_io_master.append(element)
    #    print "IO: %s" %element[1]
    else:
        rest.append(element)

# These are ready for parsing
urls = dict()
urls["raw_files"] = raw_files
urls["gists"] = gists # will parse later
urls["repos"] = inputs
urls["github_io"] = github_io_master # we can't obtain specific repos
urls["github_help"] = github_help
urls["github_users"] = users
urls["nbviewer"] = nbviewer # will parse later
pickle.dump(urls,open("%s/inputs_categorized.pkl" %outfolder,"wb"))

# For github_io urls, we need to convert to repo url
while len(github_io) > 0:
    element = github_io.pop()
    url = element[1].replace("http://","").replace("https://","")
    user_name =  url.split("/")[0].split(".")[0]
    repo_name = url.split("/")[1]
    new_url = "http://www.github.com/%s/%s" %(user_name,repo_name)
    response = requests.get(new_url)
    if response.status_code == 200:
        element = (element[0],new_url)
        urls["repos"].append(element)
    else:
        rest.append(element)

# Manual curation


pickle.dump(urls,open("%s/inputs_categorized.pkl" %outfolder,"wb"))



jobfile = "%s/parsereopos.job" %(scripts)
filey = open(jobfile,'w')


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
