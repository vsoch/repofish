from glob import glob
import pickle
import pandas
import numpy
import json
import os
import re

home = os.environ["HOME"]
base = "%s/data/pubmed" %os.environ["LAB"]
method_folder = "%s/methods" %(base)
repo_folder = "%s/repos" %(base)

files = glob("%s/*.json" %repo_folder)

# KEYWORDS
urls = []
pmids = []
keywords = []
for f in files:
    print "Adding %s to list" %(f)
    result = json.load(open(f,'r'))
    pubmed_paper = str(result["pmid"])
    urls = urls + result["github"]
    if "keywords" in result:
        if not isinstance(result["keywords"],list):
            kw = [result["keywords"]]
        else:
            kw = result["keywords"]
        keywords = keywords + kw
    
keywords = numpy.unique(keywords).tolist()

# Some keywords are in italic
keywords_updated = []
for kw in keywords:
    if isinstance(kw,dict):
        if "italic" in kw:
            if "named-content" in kw["italic"]:
                word = keywords[0]["italic"]["named-content"]["named-content"]["#text"]
                keywords_updated.append(word)
    else:
        keywords_updated.append(kw)


df=pandas.DataFrame()
df["keywords"] = keywords_updated
df.to_csv("%s/keywords_unique.tsv" %base,sep="\t",encoding="utf-8")
df.to_json("%s/keywords_unique.json" %base)

# JOURNALS
journals = []
for f in files:
    print "Adding %s to list" %(f)
    result = json.load(open(f,'r'))
    pubmed_paper = str(result["pmid"])
    urls = urls + result["github"]
    if "journal" in result:
        journals.append(result["journal"])

journals = numpy.unique(journals).tolist()
df=pandas.DataFrame(0,index=journals,columns=["count"])
for f in files:
    print "Adding %s to list" %(f)
    result = json.load(open(f,'r'))
    if "journal" in result:
        df.loc[result["journal"],"count"] = df.loc[result["journal"],"count"] + 1

df.to_csv("%s/journals_count.tsv" %base,sep="\t")
df.to_json("%s/journals_count.json" %base)
