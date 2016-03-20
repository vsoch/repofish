from Bio import Entrez
from cognitiveatlas.api import get_concept
import pickle
import json
import time
import os
import sys

def save_json(json_obj,output_file):
    filey = open(output_file,'wb')
    filey.write(json.dumps(json_obj, sort_keys=True,indent=4, separators=(',', ': ')))
    filey.close()
    return output_file


def find_files(basepath,extension=[".py"]):
    '''find_files return directories (and sub) starting from a base
    :param extension: a list of extensions to search for
    '''
    if not isinstance(extension,list):
        extension = [extension]
    files = []
    for root, dirnames, filenames in os.walk(basepath):
        new_files = ["%s/%s" %(root,f) for f in filenames if os.path.splitext(f)[-1] in extension]
        files = files + new_files
    return files


def search_pubmed(term,retstart=0,retmax=100000):
    '''search_pubmed returns a record for a search term using Entrez.esearch
    :param term: the term to search for
    :param retstart: where to start retrieving results, default is 0
    :param retmax: the max number of results to return, default is 100K
    '''
    handle = Entrez.esearch(db='pubmed',term=str(term),retstart=retstart,retmax=retmax)
    record = Entrez.read(handle)
    handle.close()
    return record

def search_articles(email,term,retmax=100000):
    '''search_articles returns a list of articles associated with a term
    :param email: an email address to associated with the query for Entrez
    :param term: the search term for pubmed, "+" will replace spaces
    :param retmax: maximum number of results to return, default 100K. If more exist, will be obtained.
    '''
    Entrez.email = email
    # Replace spaces in term with +
    term = term.replace(" ","+")
    record = search_pubmed(term)
    if "IdList" in record:
        number_matches = int(record["Count"])
        allrecords = record["IdList"]
        start = 100000
        # Tell the user this term is going to take longer
        if number_matches >= 100000:
            print "Term %s has %s associated pmids" %(term,number_matches)
        while start <= number_matches:
            record = search_pubmed(term,retstart=start)
            allrecords = allrecords + record["IdList"]
            start = start + 100000
            time.sleep(0.5)
        return allrecords
    else:
        return []


