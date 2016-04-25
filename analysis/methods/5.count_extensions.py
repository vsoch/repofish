from repofish.github import count_extensions, names_from_url
import pickle
import pandas
import sys
import os

pmid = sys.argv[1]
repo_url = sys.argv[2]
output_folder = sys.argv[3]

# We are also interested in these "special files" (note that leaving out the extensions specifies that capitalization and extension are not important)
special_files = ["README","LICENSE","circle.yml",".travis.yml","AUTHORS","CONTRIBUTING","appveyor.yml"]

user_name,repo_name = names_from_url(repo_url)
output_file = "%s/%s_%s_%s_extcounts.tsv" %(output_folder,pmid,user_name,repo_name)
if not os.path.exists(output_file):
    counts = count_extensions(repo_url,special_files=special_files)
    counts.to_csv(output_file,sep="\t")
