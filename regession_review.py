#!/usr/bin/python3
import requests
import json
import pdb
import re

BASE_API_URL = "https://openqa.suse.de/api/v1"

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

def getJobs(build, groupid):
	payload = { "build" : build, "groupid" : groupid }
	req = requests.get(BASE_API_URL + "/jobs", params=payload)
	req = req.json()
	return req["jobs"] # There is only "jobs" in there

def getLabelComment(jobid):
	req = requests.get(BASE_API_URL + "/jobs/" + jobid + "/comments")
	req = req.json()
	if len(req) >= 1:
		return req[0]["renderedMarkdown"].replace("\n", "").strip()
	else:
		return ""

def extractTrackerLink(comment):
	# TODO: replace the regex with BeautifulSoup - Because it is never, ever, on no planet in our universe, a good idea to parse html with regex…
	regex = re.search(r"""(<a).*"((http|https).*(bugzilla\.suse\.com|progress\.opensuse\.org).*?)".*?(<\/a>)""", comment)
	try:
		link = regex.group(2) # this is the big, outer match group which contains the full link
	except AttributeError: # if the regex didn't match, regex is from type None
		return comment
	else:
		return link


def getMostRecentBuild(groupid):
	# TODO: *.json routes are not considered stable - find an alternative
	req = requests.get("https://openqa.suse.de/group_overview/" + str(groupid) + ".json")
	req = req.json()
	build = req["build_results"][0]["build"]
	return build

def main():
	build = getMostRecentBuild(112)
	jobs = getJobs(build, 112)
	for job in jobs:
		result = job["result"]
		if result == "passed":
			color = bcolors.OKGREEN
		elif result == "failed":
			color = bcolors.FAIL
			trackerLink = " (" + extractTrackerLink(getLabelComment(str(job["id"]))) + ")"

		print(color + job["name"] + bcolors.ENDC + trackerLink)

		modules = job["modules"]
		for module in modules:
			color = bcolors.ENDC # default to no color
			result = module["result"]
			if result == "passed":
				color = bcolors.OKGREEN
			elif result == "failed":
				color = bcolors.FAIL
			print("\t" + color + module["name"] + bcolors.ENDC)
	pdb.set_trace()

main()
