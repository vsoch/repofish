#!/usr/bin/env python

from Bio import Entrez
import urllib2
import tarfile
import pandas
import urllib
import string
import numpy
import time
import json
import re
import sys
import os


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


def load_pmc():
    print "Downloading latest version of pubmed central ftp lookup..."
    ftp = pandas.read_csv("ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/file_list.txt",skiprows=1,sep="\t",header=None)
    ftp.columns = ["URL","JOURNAL","PMCID","PMID"]
    return ftp


def download_pubmed(pmids,ftp,download_folder):
    """download_pubmed downloads full text of articles with pubmed ids pmids to folder
    :param pmids: list of pmids to download
    :param ftp: the complete ftp object obtained with load_pmc
    :param download_folder: the folder to download to
    """
    if isinstance(pmids,str):
        pmids = [pmids]

    subset = pandas.DataFrame(columns=ftp.columns)
    for p in pmids:
        row = ftp.loc[ftp.index[ftp.PMCID == p]]
        subset = subset.append(row)
    # Now for each, assemble the URL
    for row in subset.iterrows():
        url = "ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/%s" % (row[1]["URL"])
        download_place = "%s/" %(download_folder)
        basename = os.path.basename(row[1]["URL"])
        if not os.path.isfile("%s/%s" %(download_folder,basename)):
            download_single(url,download_place)
            time.sleep(0.5)

def download_single(resource,download_folder):
    """download_single single downloads some resource with wget to folder
    :param resource: resource to download
    :param download_folder: the folder to download to
    """
    print "Downloading %s" %(resource)       
    os.system("wget \"%s\" -P %s" %(resource,download_folder))


def check_download(pmid,ftp,download_folder):
    """check_download checks if file downloaded, returns True or False
    :param pmid: the pmid to check
    :param ftp: the complete ftp object obtained with load_pmc
    :param download_folder: the folder to download to
    """
    article = ftp.loc[ftp.index[ftp.PMCID == pmid]]
    article = os.path.basename(article["URL"].tolist()[0])
    article = "%s/%s" %(download_folder,article)
    return os.path.exists(article)


def extract_xml_compressed(xmlgz,extension=".nxml"):
    '''extract_xml_compressed reads XML from compressed file
    :param xmlgz: compressed paper with xml file inside 
    '''
    tar = tarfile.open(xmlgz, 'r:gz')
    for tar_info in tar:
        if os.path.splitext(tar_info.name)[1] == extension:
            file_object = tar.extractfile(tar_info)
            return file_object.read().replace('\n', '')

'''Extract text from xml or nxml file directory'''
def read_xml(xml):
    '''read_xml reads an xml file and returns raw data
    :param xml: the xml file
    '''
    with open (xml, "r") as myfile:
        return myfile.read().replace('\n', '')


def get_xml(paper,extension=".nxml"):
    '''get_xml is a wrapper for read_xml and extract_xml_compressed
    :param paper: a pubmed (nxml) paper, either as is, or compressed.
    '''
    if re.search("[.tar.gz]",paper):
        raw = extract_xml_compressed(paper,extension=extension)
    else:
        raw = read_xml(paper)
    return raw

