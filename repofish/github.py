'''

Functions for parsing Github repositories

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

from git import Repo
from repofish.utils import find_files
import requests
import tempfile
import urllib2
import pandas
import shutil
import time
import math
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


def names_from_url(repo_url):
    '''names_from_url will return the username and repo name, given a repo url
    :param repo_url: the full url of the github repo
    '''
    if repo_url[-1] == "/":
        repo_url = repo_url[:-1]
    repo_name = repo_url.split("/")[-1]
    user_name = repo_url.split("/")[-2]
    return user_name,repo_name


def check_repo(repo):
    '''check_repo checks if a repo object is of type Repo from git, if not, attempts to make one
    :param repo: path to a local repo, a git.Repo object, or a url
    '''
    if not isinstance(repo,Repo):
        if os.path.exists("%s/.git" %(repo)):
            repo = Repo(repo)
        else:   
            repo = download_repo(repo)
    return repo

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
    iters = int(math.ceil(len(function_names)/float(limit)))
    api_working = True
    user_name,repo_name = names_from_url(repo)

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

    # Clean up
    if destination != None:
        clean_up(destination)
    return matches

def get_rate_limit(access_token):
    '''get_rate_limit uses the github api against some access_token to return a data structure for the rate limit
    :param access_token: the github access token
    '''
    url = "https://api.github.com/rate_limit?access_token=%s" %(access_token)
    headers = {'Accept': 'application/vnd.github.v3.text-match+json'}
    headers["Authorization"] = "token %s" %(access_token)
    return requests.get(url, headers=headers).json()


def search_imports(repo,extension=".py"):
    '''search_imports searches for statements like "import * from *" or import * and returns a data structure with libraries used by an application
    :param repo: either a local repo, or github repo URL
    :param extension: the extension (language) of the files to search
    '''
    user_name,repo_name = names_from_url(repo)
    repo = check_repo(repo)
    count = 0
    matches = pandas.DataFrame()

    pyfiles = find_files(repo.working_dir,extension=[extension])
    for py_file in pyfiles:

        # We will save a dataframe for just the script, and then append to matches
        single_matches = pandas.DataFrame()

        # Read the file, save some meta data for later
        filey = open(py_file,"rb")
        lines = filey.read().splitlines()
        filey.close()
        filename = os.path.basename(py_file)

        if len(lines) > 0:
            while len(lines) > 0:
                line = lines.pop(0).strip(" ")
                if re.search("import ",line):
                    # If the line ends in "/" then it's a continuation of the last line
                    while line[-1] == "/":
                        current_line = line[:-1] # remove the "/"
                        line = lines.pop(0)
                        line = "%s %s" %(current_line,line)
                    statements = line.split(" ")
                    # Remove empty statements, and if a comment is found, clip it
                    statements = [statements[x] for x in range(len(statements)) if statements[x] != ""]
                    comment_idx = [x for x in range(len(statements)) if re.search("#",statements[x])]
                    if len(comment_idx)>0:
                        statements = statements[:comment_idx[0]]
                    found_from = False
                    while len(statements) > 0: 
                        statement = statements.pop(0)
                        if statement == "from":
                            module = statements.pop(0)
                            found_from = True
                        elif statement == "import":
                            if found_from == True:
                                funcs = parse_imports(statements)
                                funcs["module_name"] = funcs.shape[0]*[module]   
                            else:
                                funcs = parse_imports(statements)
                                funcs["module_name"] = funcs["function_name"]
                            single_matches = single_matches.append(funcs)
        single_matches["filename"] = single_matches.shape[0]*[filename]
        single_matches.index = ["%s_%s_%s" %(repo_name,filename,x) for x in range(single_matches.shape[0])]
        matches = matches.append(single_matches)
    matches["repo_name"] = matches.shape[0]*[repo_name]
    matches["user_name"] = matches.shape[0]*[user_name]

    # Clean up
    clean_up(repo)
    return matches


def parse_imports(statements):
    modules = pandas.DataFrame(columns=["function_name","import_as"])
    statements = [s.strip(",").strip(" ") for s in statements]
    finished = False
    index = 0
    count = 0
    while finished == False:
        module = statements[index]
        if index!= len(statements):
            # We are at the end of the list
            if index == len(statements)-1:
                import_as = module
                finished = True
            elif statements[index+1] == "as": 
                import_as = statements[index+2]
                if (index+3) > len(statements)-1:
                    finished = True
                else:
                    index = index+3
            else:
                import_as = module
                index = index + 1

            modules.loc[count] = [module,import_as]
            count +=1
        else:
            finished = True
    return modules     

    
def clean_up(repo):
    if isinstance(repo,Repo):
        if os.path.exists(repo.working_dir):
            if re.search("^/tmp",repo.working_dir):
                shutil.rmtree(repo.working_dir)

def search_code_local(repo,search_term,repo_name,user_name,extension=".py"):
    '''search code in a local github repo
    :param repo: either a local repo, or github repo URL
    :param search_term: the text to search for in the code
    :param repo_name: name of the repo
    :param user_name: name of user that owns repo
    :param extension: the extension (language) of the files to search
    '''
    repo = check_repo(repo)
    count = 0
    matches = get_match_df()

    try:
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
    except:
        print "Problem with term %s" %(search_term)
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

def add_count(df,ridx,cidx="count",addition=1):
    '''add_count is a helper function to add count to a data frame for a particular index (extension or special file)
    :param df: the data frame to add the count to
    :param ridx: the x (row) index to add to
    :param cidx: the y (columns) index to add to
    :param addition: the number to add to the count
    '''
    if ridx in df.index:
        df.loc[ridx,cidx] += addition
    else: 
        df.loc[ridx,cidx] = addition
    return df

def count_extensions(repos,special_files=None):
    '''count_extensions counts the number of extensions in one or more repos, along with special files (license, readme, etc)
    :param repos: a list of one or more repos to count
    :param special_files: a list of special files to count as well. Do not specify extension to allow any
    '''
    if isinstance(repos,str):
        repos = [repos]

    special_file_re = "|".join(special_files)
    
    # We will index special files based on filename only
    countdf = pandas.DataFrame(columns=["count"])

    for repo in repos:
        user_name,repo_name = names_from_url(repo)
        repo = check_repo(repo)
        files = find_files(repo.working_dir,any_extension=True)
        for filepath in files:
            _,filename = os.path.split(filepath) 

            # First look for special files
            if re.search(special_file_re,filename):
                special_index = os.path.splitext(filename)[0]
                countdf = add_count(countdf,special_index)

            # Now count extension
            ext = ''.join(os.path.splitext(filename)[1:])
            if ext == '':
                ext = 'NOEXTENSION'
            countdf = add_count(countdf,ext)

    return countdf

