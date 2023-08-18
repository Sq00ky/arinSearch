#!/usr/bin/python3
import argparse
from requests import *
import json

#
# Thanks to @MuirlandOracle for helping solve an issue where data would be converted to a list (ew) instead of a JSON object. 
#

# Variables
orgList = []
netBlock = []
totalOrgList = 0
addressRangesFound = 0

args = argparse.ArgumentParser(description="", formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)
args.add_argument('-s', '--search', dest='search', required=True, default=None,help='The name of the company you would like to search for.')
args.add_argument('-v', '--verbose', dest='verbose', action="store_true", default=False,help='The name of the company you would like to search for.')

args = args.parse_args()

searchString = utils.quote(args.search)
urlToSearch = "http://whois.arin.net/rest/orgs;name=" + searchString + "*"

# Query the ARIN API to search for companies
r = get(urlToSearch, headers={'Accept': 'application/json'})
if("Your search did not yield any results." in str(r.content)):
	print("No companies found. Exiting...")
	exit(1)
try:
	jsonData = r.json()
except Exception as e:
	print("An error occured decoding JSON data: " + str(e))
	print(r.text)
	exit(1)


if(args.verbose == True):
	print(json.dumps(jsonData, indent=2))

compData = jsonData["orgs"]["orgRef"]
if not isinstance(compData, list): compData = [compData]
for COMP in compData:
	orgList.append(COMP["@handle"])
	totalOrgList += 1

print("Total orgs extracted:", totalOrgList)
print("Finding IP address ranges...")

for val in orgList:
	if(args.verbose == True):
		print("Org: " + str(val))
	urlToSearch = "http://whois.arin.net/rest/org/" + val.strip("\n") + "/nets"
	r = get(urlToSearch, headers={'Accept': 'application/json'})
	if ("No related resources were found for the handle provided" in str(r.content)):
		continue
	try:
		jsonData = r.json()
		netData = jsonData["nets"]["netRef"]
        # Ensure that we are always working with a list
		if not isinstance(netData, list): netData = [netData]
		for net in netData:
			if "::" in net["@startAddress"]:
				continue
			print("Address Range: " + net["@startAddress"] + "-"+ net["@endAddress"] )
			addressRangesFound += 1

	except Exception as e:
		print("Error, could not decode JSON: "+ str(e))
		#print("DEBUG Content Response: " + str(r.content))
		print(jsonData)
print("Total address ranges found: ", addressRangesFound)
