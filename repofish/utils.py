'''

Copyright (c) 2016-2018 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

import unicodedata
import pickle
import json
import time
import os
import sys

def save_json(json_obj, output_file, mode='w'):
    with open(output_file, mode) as filey:
        filey.writelines(json.dumps(json_obj, sort_keys=True,indent=4, separators=(',', ': ')))
    return output_file

def save_txt(text, filename, mode="w"):
    with open(filename, mode) as filey:
        filey.writelines(text)
    return filename

def convert_unicode(unicode_str, to="ascii", ignore=False, replace_with=" "):
    '''replace_unicode will return a string version of a unicode string, with unicode characters replaced

       Paramters
       =========   
       unicode_str: unicode string
       to: format to convert to (default is ascii)
       ignore: ignore characters that can't be converted to "to" format (eg, replace with "") default False
       replace_with: if ignore=False, string content to replace with (default is space)
       result: the converted string

    '''
    ignore_option = 'ignore'
    if not ignore:
        ignore_option = 'replace'

    result = unicodedata.normalize('NFKD',unicode_str).encode(to, ignore_option)
    if not ignore:
        result = result.replace("?", replace_with)
    return result

def find_files(basepath,extension=[".py"],any_extension=False):
    '''find_files return directories (and sub) starting from a base

       Parameters
       ==========
       extension: a list of extensions to search for
    '''
    if not isinstance(extension,list):
        extension = [extension]

    files = []
    for root, dirnames, filenames in os.walk(basepath):
        if not any_extension:
            new_files = ["%s/%s" %(root,f) for f in filenames if os.path.splitext(f)[-1] in extension]
        else:
            new_files = ["%s/%s" %(root,f) for f in filenames]
        files = files + new_files
    return files
