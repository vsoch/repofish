# Here we want to extract equations from wikipedia article pages

from repofish.wikipedia import get_page
from repofish.utils import save_json, save_txt
from BeautifulSoup import BeautifulSoup
import pandas
import json
import time
import re

methods = pandas.read_csv("wikipedia_methods.tsv",sep="\t",index_col=0)
skip = ['1.96','PARAFAC','Safety in numbers','T distribution (disambiguation)']

results = dict()

for method in methods["methods"]:
    if method not in results and method not in skip:
        print "Extracting equations from %s" %(method)
        result = get_page(method)
        html = result.html()
        soup = BeautifulSoup(html)

        equations = []

        # Equations are represented as images
        images = soup.findAll('img')
        for image in images:
            image_class = image.get("class")
            if image_class != None:
                if re.search("tex|math",image_class):
                    png = image.get("src")
                    tex = image.get("alt")
                    entry = {"png":png,
                             "tex":tex}
                    equations.append(entry)

        if len(equations) > 0:
            results[method] = equations
        else:
            skip.append(method)

save_json(results,"wikipedia_equations.json")
