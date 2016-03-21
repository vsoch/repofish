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
