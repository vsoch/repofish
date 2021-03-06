from xml.parsers.expat import ExpatError
from repofish.pubmed import get_xml
from glob import glob
import xmltodict
import pandas
import pickle
import numpy
import json
import sys
import os
import re

# Here is the path to the folder with xml files
article_folder = sys.argv[1]
output_dir = sys.argv[2]

# Read in our terms
xmls = glob("%s/*.nxml" %article_folder)

for xml_file in xmls:
    text = get_xml(xml_file)
    valid = True
    try:
        xml = xmltodict.parse(text)
    except ExpatError:
        print "Invalid format xml for %s" %(xml_file)
        valid = False

    res = dict()

    # Does the text have github repos somewhere?
    if re.search("github",text):

        # First try to parse from xml
        if valid == True:
            try:
                article_meta = xml["article"]["front"]['article-meta']
                journal_meta = xml["article"]["front"]["journal-meta"]
                # Save information to result object, will be saved as json
 
                # TITLE
                res["title"] = article_meta['title-group']['article-title']
                if isinstance(res["title"],dict):
                    res["title"] = res["title"]["#text"]

                # JOURNAL
                try:
                    res["journal"] = journal_meta["journal-id"][0]["#text"]
                except:
                    res["journal"] = os.path.basename(article_folder).replace("_"," ")            

                # PMID
                try:
                    res["pmid"] = [x["#text"] for x in xml["article"]["front"]['article-meta']['article-id'] if x["@pub-id-type"]=="pmid"][0]
                except:
                    res["pmid"] = os.path.basename(zip_file).split(".")[0]

                authors = []
                if isinstance (article_meta['contrib-group'],dict):
                    if "contrib" in article_meta['contrib-group']:
                        for x in article_meta['contrib-group']['contrib']:
                            if isinstance(x,dict):
                                if x["@contrib-type"]=="author":
                                    authors.append("%s %s" %(x["name"]['given-names'],x["name"]["surname"]))
                # Article subject tags
                subjects = xml["article"]["front"]['article-meta']['article-categories']['subj-group']
                if isinstance(subjects,list):
                    res["subjects"] = [x['subject'] for x in subjects]
                else:
                    res["subjects"] = [subjects["subject"]]
                res["keywords"] = []
                if "kwd-group" in article_meta:
                    if "kwd" in article_meta["kwd-group"]:
                        res["keywords"] = article_meta["kwd-group"]['kwd']
                if "counts" in article_meta:
                    if "equation-count" in article_meta['counts']:
                        res["equation_count"] = article_meta['counts']['equation-count']["@count"]

            except:
                pass

        # Otherwise, just try to get minimal information from text
        if "pmid" not in res:
            res["pmid"] = find_tag(text,'"pmid">\d{8}</article-id>')
        if "journal" not in res:
            res["journal"] = find_tag(text,'<journal-title *[^>]*>.*</journal-title>')
        if "keywords" not in res:
            try:
                res["keywords"] = [x.replace("<kwd>","").replace("</kwd>","")  for x in find_tag(text,'<kwd>[\w|\s]+</kwd>',single=False)]
            except:
                pass
            
        output_file = "%s/%s.json" %(output_dir,res["pmid"])

        # Find all links
        links = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        # Remove any remaining < from the urls
        links = [l.split("<")[0].strip() for l in links]
        # Get rid of trailing slashes
        links = numpy.unique([l[:-1] if l[-1]=="/" else l for l in links]).tolist()
        res["github"] = [l for l in links if re.search("github",l)]
        res["links"] = links
        filey = open(output_file,'wb')
        filey.write(json.dumps(res, sort_keys=True,indent=4, separators=(',', ': ')))
        filey.close()
    else:
        print "ARTICLE %s DOES NOT HAVE GITHUB LINKS" %(xml_file)


def find_tag(text,regexp,single=True):
    match = re.findall(regexp,text)
    if len(match) > 0:
        if single == True:
            match =  [x for x in match[0].split(">") if len(x)>0][-1].split("</")[0]        
    return match
