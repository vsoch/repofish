# Functions for parsing github repos

import pandas
import urllib2
import requests
import time
import numpy
import json
import re

def get_match_df():
    column_names = ['file_name',
                    'user_name',
                    'repo_name',
                    'url_json',
                    'url_html',
                    'score',
                    'text_match']
    return pandas.DataFrame(columns=column_names)


def search_code(repo,function_names,limit=10):
    matches = get_match_df()
    iters = int(numpy.ceil(len(function_names)/10.0))
    for i in range(iters):
        start = i*limit
        if (start + limit) < len(function_names):
            end = start + limit
        else:
            end = len(function_names)
        batch = function_names[start:end]
        for function_name in batch:
            try:
                match = search_code(repo,function_name,access_token)
                matches = matches.append(match)
            except:
                print "Error search for %s in %s" %(function_name,repo)
        time.sleep(60)


def search_code_single(repo,search_term,language="python",access_token=None):
    '''search code in a github repo
    :param repo: should be the username/reponame or full url
    :param search_term: the text to search for in the code
    :param language: the language of the files to search
    '''
    count = 0
    matches = get_match_df()
    repo_name = repo.split("/")[-1]
    user_name = repo.split("/")[-2]
    url = "https://api.github.com/search/code?q=%s+in:file+language:%s+repo:%s/%s" %(search_term,language,user_name,repo_name)
    headers = {'Accept': 'application/vnd.github.v3.text-match+json'}
    if access_token != None:
        headers["Authorization"] = "token %s" %(access_token)
    r = requests.get(url, headers=headers).json()
    if r["total_count"] > 0:
        for item in r["items"]:
            for match in item["text_matches"]:
                match_list = [item["name"],user_name,repo_name,item["url"],item["html_url"],item["score"],match["fragment"]]
                matches.loc["%s/%s_%s" %(user_name,repo_name,count)] =  match_list
                count+=1
    print "Found %s results for %s in %s" %(count,search_term,repo_name)
    return matches
    

def find_repos(search_term,language="python"):
    print "WRITE ME"

#curl -H 'Accept: application/vnd.github.v3.text-match+json' \
#  'https://api.github.com/search/repositories?q=tetris+language:assembly&sort=stars&order=desc'

# First find repos
#https://api.github.com/search/repositories?q=scikit-learn+language:python&sort=stars&order=desc

# Then search code
        
