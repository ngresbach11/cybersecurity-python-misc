# Script to take a csv containing a list of vulnerabilities and automatically manage jira tickets for each vulnerability.
# Opens one ticket per overall vulnerability, with all affected IPs included in the description of that ticket.
# Requires python jira library

from jira import JIRA
import csv
from datetime import date

today = date.today()
options = {'server': 'http://192.168.0.60:8080'}
apiKey = '[REDACTED]'
jira = JIRA(options, basic_auth=('[loginusername]', apiKey))

existingIssues = []
jiraDict = {}
listOfVulns = []
issuesDict = {}
allHosts = []
critialCount = 0
highCount = 0
medCount = 0
lowCount = 0
issuesOpened = 0
issuesClosed = 0

def closeIssues():
    issuesToClose = list(set(existingIssues) - set(listOfVulns))
    for item in issuesToClose:
        issue = jira.issue(jiraDict[item])
        if issue.fields.status != "Done":
            jira.transition_issue(jiraDict[item], "Done")
            print(jiraDict[item], "has been closed.")
            global issuesClosed
            issuesClosed = issuesClosed + 1 # Iterate for issue closed

def readCSVReport():
    with open("samplecsvvulncsv.csv", "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        for line in csv_reader:
            if line[1] not in listOfVulns:
                listOfVulns.append(line[1])
                issuesDict[line[1]] = line[3] + ". Affected IPs: " + line[2]
            else:
                issuesDict[line[1]] += ", " + line[2]
            if line[4] == "Critical": # Metrics stuff
                global critialCount
                critialCount = critialCount + 1
            elif line[4] == "High":
                global highCount
                highCount = highCount + 1
            elif line[4] == "Medium":
                global medCount
                medCount = medCount + 1
            elif line[4] == "Low":
                global lowCount
                lowCount = lowCount + 1
            if line[2] not in allHosts: # Used for CCRI score
                allHosts.append(line[2])

def appendExistingTickets():
    for singleIssue in jira.search_issues(jql_str='project = vuln'):
        existingIssues.append(singleIssue.fields.summary)
        jiraDict[singleIssue.fields.summary] = singleIssue.key
        # Need to do this to map issues to their keys so I can update, autocomplete, etc

def openNewIssues(issueName, issueDescription):
    if issueName not in existingIssues:
        print("Creating " + issueName + " : " + issueDescription)
        issue_dict = {
        'project': {'key': 'VULN'},
        'summary': issueName,
        'description': issueDescription,
        'issuetype': {'name': 'Bug'},
        }
        new_issue = jira.create_issue(fields=issue_dict) # Creates a new issue
        global issuesOpened
        issuesOpened = issuesOpened + 1 # Iterate for new issue opened this run
    else:
        issueToUpdate = jira.issue(jiraDict[issueName])
        issueToUpdate.update(fields={'description': issueDescription})
        print("Updating " + issueName + " : " + issueDescription)

def logMetrics():
    with open("metrics.csv", mode="a") as csvfile:
        fieldnames = ['date','criticals', 'highs', 'meds', 'lows', 'ccri', 'deltaopened', 'deltaclosed']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        numOfHosts = len(allHosts)
        ccriScore = (((critialCount + highCount) * 10 + (medCount * 4) + lowCount) / 15 ) / numOfHosts # May need to fix this if the forumula is off
        writer.writerow({'date': date.today(), 'criticals': critialCount, 'highs': highCount, 'meds': medCount, 'lows': lowCount, 'ccri': ccriScore, 'deltaopened': issuesOpened, 'deltaclosed': issuesClosed})

if __name__ == "__main__":
    appendExistingTickets()
    readCSVReport()
    i = 0
    for vuln in listOfVulns:
        openNewIssues(listOfVulns[i], issuesDict[listOfVulns[i]])
        i = i + 1
    closeIssues()
    logMetrics()