#!/usr/bin/env python3

import sys
import whois
from time import sleep
from tqdm import tqdm
from re import findall
from json import loads
from requests import get
from urllib.parse import quote_plus
from argparse import ArgumentParser
from configparser import RawConfigParser
from concurrent.futures import ThreadPoolExecutor, as_completed


def printDomainInfo(domain):
	w = whois.whois(domain)

	regOrg = findall("Registrant\sOrgani[sz]ation:\s(.*?)\r?\n", w.text)
	if regOrg:
		regOrg = regOrg[0]

	regName = findall("Registrant\sName:\s(.*?)\r?\n", w.text)
	if regName:
		regName = regName[0]

	regEm = findall("Registrant\sEmail:\s(.*?)\r?\n", w.text)
	if regEm:
		regEm = regEm[0]

	print(f"[1] Company Name: '{regOrg}'")
	print(f"[2] Owner Name: '{regName}'")
	print(f"[3] Email Address: '{regEm}'")
	print(f"[>] Use -c and one of the numbers above or see the help.")


def getDomainQueryString(domain, choice):
	w = whois.whois(domain)

	if choice == "1":
		regOrg = findall("Registrant\sOrgani[sz]ation:\s(.*?)\r?\n", w.text)
		if regOrg:
			return regOrg[0]

	if choice == "2":
		regName = findall("Registrant\sName:\s(.*?)\r?\n", w.text)
		if regName:
			return regName[0]

	if choice == "3":
		regEm = findall("Registrant\sEmail:\s(.*?)\r?\n", w.text)
		if regEm:
			return regEm[0]


def verifyInput(args):
	if not args.domain and not args.compName and not args.ownName and not args.email:
		print("[-] Please provide arguments or -h for help")
		parser.print_usage()
		exit(1)


def getPageResults(url, page):
	urlToRun = f"{url}&page={page}"
	totalPages = 0
	results = []

	response = get(urlToRun)
	jsonResp = loads(response.text)

	if jsonResp["status"] == 1:
		totalPages = jsonResp["total_pages"]
		for item in jsonResp["search_result"]:
			results.append(item["domain_name"])

	else:
		pass

	return totalPages, list(set(results))


def gatherFromWhoxy(baseUrl):
	allResults = []
	page = 1
	totalPages = 99999

	while page <= totalPages:
		totalPages, runResults = getPageResults(baseUrl, page)
		allResults.extend(runResults)
		page += 1

	return(set(list(allResults)))


def processDomain(domain, queryString, sleepTime):
	if sleepTime > 0: 
		sleep(sleepTime)

	try:
		w = whois.whois(domain, quiet=True)

		if queryString in w.text:
			return domain
		else:
			return None

	except whois.parser.PywhoisError:
		pass


def pickUrl(choice, whoxyKey, queryString):
	if choice == "1":
		return f"http://api.whoxy.com/?key={whoxyKey}&reverse=whois&mode=micro&company={quote_plus(queryString)}"

	elif choice == "2":
		return f"http://api.whoxy.com/?key={whoxyKey}&reverse=whois&mode=micro&name={quote_plus(queryString)}"

	elif choice == "3":
		return f"http://api.whoxy.com/?key={whoxyKey}&reverse=whois&mode=micro&email={quote_plus(queryString)}"


def defineVars(args):
	if args.domain and not args.choice:
		printDomainInfo(args.domain)
		exit(0)

	elif args.domain and args.choice:
		choice = args.choice
		queryString = getDomainQueryString(args.domain, choice)

	elif args.compName:
		choice = "1"
		queryString = args.compName

	elif args.ownName:
		choice = "2"
		queryString = args.ownName

	elif args.email:
		choice = "3"
		queryString = args.email

	return choice, queryString


def handleOutput(outputFile, results):
	if outputFile:
		with open(args.outputFile, "w") as outfile:
			for item in results:
				sys.stdout.write(f"{item}\n")
				outfile.write(str(f"{item}\n"))

	else:
		for item in results:
			sys.stdout.write(f"{item}\n")


if __name__=="__main__":
	parser = ArgumentParser(prog="WhoxySD.py", description="Gather all root domains of an organization from Whoxy")
	parser.add_argument("-d", "--domain", action="store", dest="domain", help="Domain to get details for", type=str, default=None)
	parser.add_argument("-c", "--choice", action="store", dest="choice", help="Choices, for use with -d: [1=cn, 2=on, 3=em]", type=str, default=None, choices=["1","2","3"])
	parser.add_argument("-cn", "--company-name", action="store", dest="compName", help="Company name to look for", type=str, default=None)
	parser.add_argument("-on", "--owner-name", action="store", dest="ownName", help="Owner name to look for", type=str, default=None)
	parser.add_argument("-em", "--email", action="store", dest="email", help="Email to look for", type=str, default=None)
	parser.add_argument("-o", "--output", action="store", dest="outputFile", help="Output file", type=str, default=None)
	parser.add_argument("-t", "--threads", action="store", dest="threads", help="Number of threads [default is 1]", type=int, default=1)
	parser.add_argument("-s", "--sleep", action="store", dest="sleepTime", help="Sleep in secs between iterations [default is 0]", type=int, default=0)
	parser.add_argument("-q", "--quiet", action="store_true", dest="quiet", help="If enabled, only found domains are printed", default=False)
	args = parser.parse_args()
	verifyInput(args)

	parser = RawConfigParser()
	parser.read(f"{sys.path[0]}/config.ini")
	whoxyKey = parser.get("Whoxy", "WHOXY_API_KEY")

	choice, queryString = defineVars(args)
	url = pickUrl(choice, whoxyKey, queryString)

	whoxyResults = gatherFromWhoxy(url)

	finalResults = []
	with tqdm(total = len(whoxyResults), disable=args.quiet) as pbar:
		with ThreadPoolExecutor(max_workers=args.threads) as executor:
			futures = [executor.submit(processDomain, domain, queryString, args.sleepTime) for domain in whoxyResults]

			for future in as_completed(futures):
				if future.result():
					finalResults.append(future.result())

				pbar.update(1)

	if not args.quiet: 
		print(f"Results from Whoxy: {len(whoxyResults)}")
		print(f"Verified results: {len(finalResults)}")

	handleOutput(args.outputFile, finalResults)
