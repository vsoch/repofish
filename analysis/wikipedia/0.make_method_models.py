
from exceptions import KeyError
from repofish.wikipedia import get_page
from repofish.utils import save_json
import pandas
import time


methods_url = "https://en.wikipedia.org/wiki/List_of_statistics_articles"
topic = "List_of_statistics_articles"
result = get_page(topic)

# Save list of methods in case it changes
methods = pandas.DataFrame()
methods["methods"] = result.links

# This is manual parsing to resolve disambiguation errors
methods[methods.methods=="A posteriori probability (disambiguation)"] = "posterior probability"
methods[methods.methods=="ANCOVA"] = "Analysis of covariance" # ANCOVA would return "Angola"
methods[methods.methods=="Data generating process"] = "data collection"
methods[methods.methods=="Data generating process (disambiguation)"] = "data collection"

methods.to_csv("wikipedia_methods.tsv",sep="\t",encoding="utf-8")

# Now let's generate a data structure with all content, links, etc.
results = dict()

for method in methods["methods"]:
    if method not in results:
        entry = {}
        result = get_page(method)
        print "Matching %s to %s" %(method,result.title) # Manual checking
        entry["categories"] = result.categories
        entry["title"] = result.title
        entry["method"] = method
        # url can let us parse for equation content
        entry["url"] = result.url

        # We can use links to calculate relatedness
        try:
            entry["links"] = result.links
        except KeyError:
            entry["links"] = []

        try:
            entry["references"] = result.references
        except KeyError:
            entry["references"] = []

        # save just summary for now.
        entry["summary"] = result.summary
        entry["images"] = result.images
        results[method] = entry
        time.sleep(0.5)

save_json(results,"wikipedia_methods.json")

