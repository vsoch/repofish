from repofish.database import get_available_modules, load_module
from repofish.github import search_code
import pickle
import time
import pandas

access_token = "vanessavanessavanessa"

# Read in list of Github repos
repos_file = "/scratch/PI/russpold/data/PUBMED/repos/repos_github_pandas_df.pkl"
repos = pickle.load(open(repos_file,"rb"))

# Get available modules
modules = get_available_modules()

# An example of running locally
# repos 9935
matches = pandas.DataFrame()
seen = []
for module in modules:
    functions = load_module(module,get_names=True)
    for repo in repos:
        if repo not in seen:
            seen.append(repo)
            new_matches = search_code(repo,function_names)
            matches = matches.append(new_matches)
