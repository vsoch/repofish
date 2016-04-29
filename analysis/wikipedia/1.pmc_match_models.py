# Match sections (paragraphs) in PMC open content paper to methods models

from repofish.nlp import processText, unicode2str
from BeautifulSoup import BeautifulSoup
from xml.parsers.expat import ExpatError
from repofish.utils import save_txt
from repofish.pubmed import get_xml
from glob import glob
import xmltodict
import tempfile
import pandas
import pickle
import numpy
import json
import sys
import os
import re

xml_file = sys.argv[1]
output_dir = sys.argv[2]
words_vectors = sys.argv[3]
methods_vectors = sys.argv[4]

# This is a data frame of methods vectors, derived from word2vec model
methods = pandas.read_csv(methods_vectors,sep="\t",index_col=0)
embeddings = pandas.read_csv(words_vectors,sep="\t",index_col=0)

# We will save a data frame of methods and similarity scores for each xml text, with PMID as index
sim = pandas.DataFrame(columns=methods.index)

### FUNCTIONS ########################################################################

# A function to find a pmid tag if cannot parse xml
def find_tag(text,regexp,single=True):
    match = re.findall(regexp,text)
    if len(match) > 0:
        if single == True:
            match =  [x for x in match[0].split(">") if len(x)>0][-1].split("</")[0]        
    return match


def text2mean_vector(paragraph,vectors):
    '''text2mean_vector maps a new text (paragraph) onto vectors (a word2vec word embeddings model) by taking a mean of the vectors that are words in the text
    :param text: a beautiful soup object (text content should be in paragraph.text)
    :param vectors: a pandas data frame of vectors, index should be words in model
    '''
    words = processText(paragraph.text)
    words = [unicode2str(w) for w in words]
    words = [w for w in words if w in vectors.index.tolist()]
    if len(words) != 0:
        return vectors.loc[words].mean().tolist()
    return None


### ANALYSIS ##########################################################################

text = get_xml(xml_file)
valid = True
try:
    xml = xmltodict.parse(text)
except ExpatError:
    print "Invalid format xml for %s" %(xml_file)
    valid = False

pmid = None

# First try to parse from xml
if valid == True:
    try:
        pmid = [x["#text"] for x in xml["article"]["front"]['article-meta']['article-id'] if x["@pub-id-type"]=="pmid"][0]
    except:
        pass

# Otherwise, just try to get minimal information from text
if "pmid" == None:
    pmid = find_tag(text,'"pmid">\d{8}</article-id>')
            

output_file = "%s/%s_methods_match.tsv" %(output_dir,pmid)

if not os.path.exists(output_file):

    # Parse text into paragraphs
    soup = BeautifulSoup(text)
    paragraphs = soup.findAll('p')

    # For each paragraph, classify the text
    for p in range(len(paragraphs)):
        paragraph = paragraphs[p]
        vector = text2mean_vector(paragraph,embeddings)
        if vector != None:
            # Compare vector to all methods
            comparison = methods.copy()
            comparison.loc["COMPARATOR"] = vector
            comparison = comparison.T.corr()     
            result = comparison.loc["COMPARATOR"]       
            result = result.drop(["COMPARATOR"])
            # Save scores to df
            sim.loc["%s_%s" %(pmid,p),result.index] = result

    # Save to output folder based on the pmid
    sim.to_csv(output_file,sep="\t")    
