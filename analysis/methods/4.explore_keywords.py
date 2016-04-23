from repofish.utils import save_json
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

# Function to parse keywords
def parse_keywords(kw):
    if isinstance(kw,dict):
        if "#text" in kw:
            return kw["#text"]
        elif "italic" in kw:
            if "named-content" in kw["italic"]:
                return kw["italic"]["named-content"]["named-content"]["#text"]
            elif "#text" in kw["italic"]:
                return kw["italic"]["#text"]
            else:
                return kw["italic"]
        elif "named-content" in kw:
            if isinstance(kw["named-content"]["named-content"],dict):
                return kw["named-content"]["named-content"]["#text"]
            return kw["named-content"]["named-content"][0]["#text"]
        elif "styled-content" in kw:
            return kw["styled-content"]["#text"]
    return kw.lower().strip()

# Some keywords are in italic
keywords_updated = []
for kw in keywords:
    keywords_updated.append(parse_keywords(kw))

# Also do a count
df = pandas.DataFrame(columns=["count"])
for f in files:
    print "Adding %s to list" %(f)
    result = json.load(open(f,'r'))
    if "keywords" in result:
        if not isinstance(result["keywords"],list):
            kw_list = [result["keywords"]]
        else:
            kw_list = result["keywords"]
        for kw in kw_list:
            kw_parsed = parse_keywords(kw)
            if kw_parsed in df.index:
                df.loc[kw_parsed,"count"] = df.loc[kw_parsed,"count"] + 1
            else:
                df.loc[kw_parsed,"count"] = 1

# One badly parsed
badly_parsed = "computational biology ; protein structure prediction ; model quality assessment programs ; boltzmann distribution ; annsen's thermodynamic hypothesis ; statistical potentials ; protein backbone ; decoy sets ;"
df = df.drop([badly_parsed])
badly_parsed = [x.strip(" ") for x in badly_parsed.split(";") if x]
for bp in badly_parsed:
    if bp in df.index:
        df.loc[bp,"count"] = df.loc[bp,"count"] + 1
    else:
        df.loc[bp,"count"] = 1

# Sort by counts
df = df.sort(columns=["count"],ascending=False)
df.to_csv("%s/keywords_counts.tsv" %base,sep="\t",encoding="utf-8")
df.to_json("%s/keywords_counts.json" %base)

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


# We need a lookup, for pmids based on journal or keyword
journal_lookup = dict()
keyword_lookup = dict()

for f in files:
    print "Parsing %s" %(f)
    result = json.load(open(f,'r'))
    pmid = str(result["pmid"])
    if "journal" in result:
        journal = result["journal"]
        if journal not in journal_lookup:
            journal_lookup[journal] = [pmid]
        else:
            journal_lookup[journal].append(pmid)
    if "keywords" in result:
        if not isinstance(result["keywords"],list):
            keys = [result["keywords"]]
        else:
            keys = result["keywords"]
        for k in keys:
            kw = parse_keywords(k)
            if kw not in keyword_lookup:
                keyword_lookup[kw] = [pmid]
            else:
                keyword_lookup[kw].append(pmid)

save_json(journal_lookup,"%s/journal_lookup.json"%base)
save_json(keyword_lookup,"%s/keyword_lookup.json"%base)
