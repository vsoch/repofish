from Bio import Entrez
from cognitiveatlas.api import get_concept
import unicodedata
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


def convert_unicode(unicode_str,to="ascii",ignore=False,replace_with=" "):
    '''replace_unicode will return a string version of a unicode string, with unicode characters replaced
    :param unicode_str: unicode string
    :param to: format to convert to (default is ascii)
    :param ignore: ignore characters that can't be converted to "to" format (eg, replace with "") default False
    :param replace_with: if ignore=False, string content to replace with (default is space)
    :return result: the converted string
    '''
    if ignore == False:
        ignore_option = 'replace'
    else:
        ignore_option = 'ignore'

    result = unicodedata.normalize('NFKD',unicode_str).encode(to,ignore_option)
    if ignore == False:
        result = result.replace("?",replace_with)
    return result

def find_files(basepath,extension=[".py"],any_extension=False):
    '''find_files return directories (and sub) starting from a base
    :param extension: a list of extensions to search for
    '''
    if not isinstance(extension,list):
        extension = [extension]
    files = []
    for root, dirnames, filenames in os.walk(basepath):
        if any_extension == False:
            new_files = ["%s/%s" %(root,f) for f in filenames if os.path.splitext(f)[-1] in extension]
        else:
            new_files = ["%s/%s" %(root,f) for f in filenames]
        files = files + new_files
    return files
