# Can we generate a graph of all possible packages?
# retrieved on April 21, 2016 5:53pm

from BeautifulSoup import BeautifulSoup
import requests
import pandas

outfolder = "/home/vanessa/Documents/Dropbox/Code/Python/repofish/analysis/pypi"
url = "https://pypi.python.org/pypi/?"
response = requests.get(url)

packages = pandas.DataFrame(columns=["package","description","version"])
soup = BeautifulSoup(response.text)
rows = soup.findAll('tr')

# First row is heading
rows.pop(0)
rows.pop(-1)

for r in range(len(rows)):
    print "Parsing row %s of %s" %(r,len(rows))
    row = rows[r]
    cols = row.findAll('td')
    package_name,description = [element.text.strip() for element in cols]
    package_name,version = package_name.split("&nbsp;")
    packages.loc[r] = [package_name,description,version]

# Save to file
out_file = "%s/pypi.tsv" %outfolder
packages.to_csv(out_file,sep="\t",encoding="utf-8")
