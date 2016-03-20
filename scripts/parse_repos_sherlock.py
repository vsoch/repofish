from repofish.database import get_available_modules, load_module
from repofish.github import search_code
import pickle
import sys
import time
import pandas


access_token = sys.argv[1]
repo_url = sys.argv[2]
output_file = sys.argv[3]
pubmed_paper = sys.argv[4]

# Get available modules
modules = get_available_modules()
module_list = []

try:
    matches = pandas.DataFrame()
    for module in modules:
        functions = load_module(module,get_names=True)
        new_matches = search_code(repo_url,functions)
        matches = matches.append(new_matches)
        module_list = module_list + new_matches.shape[0]*[module]

    matches["module"] = module_list
    matches["doi"] = matches.shape[0]*[pubmed_paper]
    if matches.shape[0] != 0:
        matches.to_csv(output_file,sep="\t")
except:
    print "Repo not found."
