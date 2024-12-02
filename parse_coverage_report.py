import sys
import os
from html.parser import HTMLParser
import urllib.parse
import urllib.request

def attrs_to_dict(attrs):
    res = {}
    for name, value in attrs:
        res[name] = value
    return res

COVERAGE_FUNCTION = 1
COVERAGE_LINE = 2
COVERAGE_REGION = 3
COVERAGE_BRANCH = 4

class Coverage(HTMLParser):
    def __init__(self):
        super().__init__()
        self.found_cov_row = False
        self.coverage = []

    def handle_starttag(self, tag, attrs):
        attrs = attrs_to_dict(attrs)
        if tag == "tr" and "class" in attrs:
            cl = attrs["class"]
            if cl == "light-row-bold":
                self.found_cov_row = True

    def handle_data(self, data):
        if self.found_cov_row:
            self.coverage.append(data)

    def get(self, index):
        if self.coverage[index].startswith("- "):
            return None
        data = self.coverage[index]
        id = data.find("%")
        if id == -1:
            return 0
        data = data[:id]
        return float(data)

    def get_total(self):
        coverages = [
            self.get(COVERAGE_FUNCTION),
            self.get(COVERAGE_LINE),
            self.get(COVERAGE_REGION),
            self.get(COVERAGE_BRANCH)
        ]
        mean = 0
        len = 0
        for x in coverages:
            if x is not None:
                mean += x
                len += 1
        mean /= len
        return mean

if len(sys.argv) != 3:
    print("Usage: python3 parse_coverage_report.py <path to main index.html> <platform name>")
    sys.exit(1)
path = os.path.join(sys.argv[1], "index.html")
platform = sys.argv[2]
coverage = Coverage()
with open(path, "r") as file:
    data = file.read()
    coverage.feed(data)

# Color rules:
# Green >= 95
# Yellow >= 80
# Orange >= 65
# Red < 65

def get_badge_url(coverage, platform):
    value = coverage.get_total()
    color = "green"
    if value < 95:
        color = "yellow"
    if value < 80:
        color = "orange"
    if value < 65:
        color = "red"
    name = "Coverage (" + platform + ")"
    name = name.replace(" ", "%20")
    text = urllib.parse.quote_plus(("%.2f" % value) + "%")
    url = "https://badgen.net/static/" + name + "/" + text + "/" + color + "?icon=codecov"
    return url

def download_badge(url, platform):
    filename = "coverage-" + platform.replace(" ", "-").lower() + ".svg"
    urllib.request.urlretrieve(url, filename)

print("# Summary (" + platform + ")")
print("")
print("| Name              | Coverage |")
print("|-------------------|----------|")
print("| Function coverage |", ("%4.2f %%" % coverage.get(COVERAGE_FUNCTION)) + "  |")
print("| Line coverage     |", ("%4.2f %%" % coverage.get(COVERAGE_LINE)) + "  |")
if coverage.get(COVERAGE_REGION) is not None:
    print("| Region coverage   |", ("%4.2f %%" % coverage.get(COVERAGE_REGION)) + "  |")
if coverage.get(COVERAGE_BRANCH) is not None:
    print("| Branch coverage   |", ("%4.2f %%" % coverage.get(COVERAGE_BRANCH)) + "  |")
print("| **Average**       |", ("%4.2f %%" % coverage.get_total()) + "  |")
print("")

download_badge(get_badge_url(coverage, platform), platform)
