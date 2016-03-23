from xml.parsers.expat import ExpatError
from repofish.pubmed import get_xml
from glob import glob
import xmltodict
import os
import re
import json
import pandas
import pickle
import sys

# Here is the path to the folder with xml files
start = sys.argv[1]
end = sys.argv[2]
targz_pickle = sys.argv[3]
output_dir = sys.argv[4]

# Read in our terms
zips = pickle.load(open(targz_pickle,"rb"))

for z in range(len(zips)):
    zip_file = zips[z]
    text = get_xml(zip_file)
    valid = True
    try:
        xml = xmltodict.parse(text)
    except ExpatError:
        print "Invalid format xml for %s" %(zip_file)
        valid = False
    # Does the text have github repos somewhere?
    if re.search("github",text) and valid == True:
        article_meta = xml["article"]["front"]['article-meta']
        journal_meta = xml["article"]["front"]["journal-meta"]
        # Save information to result object, will be saved as json
        res = dict()
        # Basic meta, title, journal, pmid
        res["title"] = article_meta['title-group']['article-title']
        if isinstance(res["title"],dict):
            res["title"] = res["title"]["#text"]
        res["journal"] = journal_meta["journal-id"][0]["#text"]
        res["pmid"] = [x["#text"] for x in xml["article"]["front"]['article-meta']['article-id'] if x["@pub-id-type"]=="pmid"][0]
        output_file = "%s/%s.json" %(output_dir,res["pmid"])
        if not os.path.exists(output_file):
            res["authors"] = ["%s %s" %(x["name"]['given-names'],x["name"]["surname"]) for x in article_meta['contrib-group']['contrib'] if x["@contrib-type"]=="author"]
            # Article subject tags
            subjects = xml["article"]["front"]['article-meta']['article-categories']['subj-group']
            if isinstance(subjects,list):
                res["subjects"] = [x['subject'] for x in subjects]
            else:
                res["subjects"] = [subjects["subject"]]
            res["keywords"] = xml["article"]["front"]['article-meta']["kwd-group"]['kwd']
            if "counts" in article_meta:
                res["equation_count"] = article_meta['counts']['equation-count']["@count"]
            # Find all links
            links = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
            # Remove any remaining < from the urls
            links = [l.split("<")[0].strip() for l in links]
            # Get rid of trailing slashes
            links = [l[:-1] if l[-1]=="/" else l for l in links]
            res["github"] = [l for l in links if re.search("github",l)]
            res["links"] = links
            filey = open(output_file,'wb')
            filey.write(json.dumps(res, sort_keys=True,indent=4, separators=(',', ': ')))
            filey.close()

