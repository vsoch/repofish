# Functions for parsing github repos

from git import Repo
from repofish.utils import find_files
import requests
import tempfile
import urllib2
import pandas
import shutil
import time
import numpy
import json
import re
import os

def get_match_df():
    column_names = ['function_name',
                    'file_name',
                    'user_name',
                    'repo_name',
                    'url_json',
                    'url_html',
                    'score',
                    'text_match']
    return pandas.DataFrame(columns=column_names)


def download_repo(repo_url,destination=None):
    '''download_repo
    Download a github repo to a destination. If destination is None, temp directory is used
    :param repo_url: full path to repo
    :param destination: the full path to the destination for the repo
    '''
    if destination == None:
        destination = tempfile.mkdtemp()
    return Repo.clone_from(repo_url, destination)


def search_code(repo,function_names,limit=10):
    '''search code uses github API and local search to parse repos for functions. If the access token is run out of calls, a local folder strategy is used instead.
    :param repo: repo name, either full URL or user/reponame format
    :function_names: a list of function names to search for
    :limit: the number of searches to do before pausing for 0.5 seconds
    '''
    # Destination will be used if API limit runs out, and we need to clone locally
    destination = None
    matches = get_match_df()
    iters = int(numpy.ceil(len(function_names)/float(limit)))
    api_working = True

    # Will be passed to local function, if needed
    if repo[-1] == "/":
        repo = repo[:-1]
    repo_name = repo.split("/")[-1]
    user_name = repo.split("/")[-2]

    for i in range(iters):
        start = i*limit
        if (start + limit) < len(function_names):
            end = start + limit
        else:
            end = len(function_names)
        batch = function_names[start:end]
        for function_name in batch:
            if api_working == True:
                try:
                    # If the auth_token works
                    match = search_code_single(repo,function_name,access_token)
                except:
                    api_working = False
                    print "API credentials not working, will parse local repo instead."
                    destination = download_repo(repo)
                    match = search_code_local(destination,function_name,repo_name,user_name)
            else:
                    match = search_code_local(destination,function_name,repo_name,user_name)

            matches = matches.append(match)

    # If the folder exists, delete it
    if destination != None:
        if isinstance(destination,Repo):
            if os.path.exists(destination.working_dir):
                shutil.rmtree(destination.working_dir)
    return matches

def get_rate_limit(access_token):
    url = "https://api.github.com/rate_limit?access_token=%s" %(access_token)
    headers = {'Accept': 'application/vnd.github.v3.text-match+json'}
    headers["Authorization"] = "token %s" %(access_token)
    return requests.get(url, headers=headers).json()


def search_code_local(repo,search_term,repo_name,user_name,extension=".py"):
    '''search code in a local github repo
    :param repo: either a local repo, or github repo URL
    :param search_term: the text to search for in the code
    :param repo_name: name of the repo
    :param user_name: name of user that owns repo
    :param extension: the extension (language) of the files to search
    '''
    if not isinstance(repo,Repo):
        if os.path.exists("%s/.git" %(repo)):
            repo = Repo(repo)
        else:   
            repo = download_repo(repo)

    count = 0
    matches = get_match_df()
    pyfiles = find_files(repo.working_dir,extension=[extension])
    for py_file in pyfiles:

        # Read the file, save some meta data for later
        filey = open(py_file,"rb")
        lines = filey.read().splitlines()
        filey.close()
        filename = os.path.basename(py_file)

        if len(lines) > 0:
            for l in range(len(lines)):
                line = lines[l]

                # If we find the search term, take line and following
                if re.search(str(search_term),line):
                    if l != len(lines):
                        fragment = lines[l:l+1]
                    else:
                        fragment = line

                    # Add to the matches data frame
                    match_list = [search_term,filename,user_name,repo_name,None,None,None,fragment]
                    matches.loc["%s/%s_%s" %(user_name,repo_name,count)] =  match_list
                    count+=1
    
    print "Found %s results for %s in %s" %(count,search_term,repo_name)
    return matches


def search_code_single(repo,search_term,language="python",access_token=None):
    '''search code in a github repo using Github API
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
                match_list = [search_term,item["name"],user_name,repo_name,item["url"],item["html_url"],item["score"],match["fragment"]]
                matches.loc["%s/%s_%s" %(user_name,repo_name,count)] =  match_list
                count+=1
    print "Found %s results for %s in %s" %(count,search_term,repo_name)
    return matches
