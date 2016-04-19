from repofish.github import search_imports
import pickle
import pandas
import sys
import os

repo_url = sys.argv[1]
output_file = sys.argv[2]
pubmed_paper = sys.argv[3]

if not os.path.exists(output_file):
    try:
        matches = search_imports(repo_url,extension=".py")
        matches["doi"] = matches.shape[0]*[pubmed_paper]
        if matches.shape[0] != 0:
            matches.to_csv(output_file,sep="\t")
            print "Found results for %s" %(repo_url)
        else:
            print "No matches found for %s." %(repo_url)
    except:
        print "Error parsing imports for %s" %(repo_url)


