from repofish.github import search_imports
import pickle
import pandas
import sys

repo_url = sys.argv[1]
output_file = sys.argv[2]
pubmed_paper = sys.argv[3]

try:
    matches = search_imports(repo_url,extension=".py")
    matches["doi"] = matches.shape[0]*[pubmed_paper]
    if matches.shape[0] != 0:
        matches.to_csv(output_file,sep="\t")
    else:
        print "No matches found for repo."
except:
    print "Error parsing imports for repo."
