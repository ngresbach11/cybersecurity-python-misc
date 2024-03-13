# Script to take a csv containing a list of vulnerabilities and automatically manage jira tickets for each vulnerability.
# Opens one ticket per overall vulnerability, with all affected IPs included in the description of that ticket.
# Requires python jira library

from jira import JIRA
import csv

options = {'server': 'http://192.168.0.60:8080'} # replace this with jira server instance
jira = JIRA(options, basic_auth=('[USERNAMEHERE]', '[PASSWORDHERE]')) # Many different forms of authentication can be used here, leaving basic auth for simplicity. https://jira.readthedocs.io/examples.html#authentication

existingIssues = []
jiraDict = {}
listOfVulns = []
issuesDict = {}

def closeIssues():
    issuesToClose = list(set(existingIssues) - set(listOfVulns))
    for item in issuesToClose:
        issue = jira.issue(jiraDict[item])
        if issue.fields.status != "Done":
            jira.transition_issue(jiraDict[item], "Done") # Moves ticket to "Done"
            print(jiraDict[item], "has been closed.")

def readCSVReport():
    with open("samplecsvvulncsv.csv", "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        for line in csv_reader:
            if line[1] not in listOfVulns:
                listOfVulns.append(line[1])
                issuesDict[line[1]] = line[3] + ". Affected IPs: " + line[2] # Replace these for how your .csv is setup
            else:
                issuesDict[line[1]] += ", " + line[2]

def appendExistingTickets():
    for singleIssue in jira.search_issues(jql_str='project = vuln'):
        existingIssues.append(singleIssue.fields.summary)
        jiraDict[singleIssue.fields.summary] = singleIssue.key
        # Need to do this to map issues to their keys so I can update, autocomplete, etc

def openNewIssues(issueName, issueDescription):
    if issueName not in existingIssues:
        print("Creating " + issueName + " : " + issueDescription)
        issue_dict = {
        'project': {'key': 'VULN'}, # This is the project key you set when you create a project in jira.
        'summary': issueName,
        'description': issueDescription,
        'issuetype': {'name': 'Bug'},
        }
        new_issue = jira.create_issue(fields=issue_dict) # Creates a new issue
    else:
        issueToUpdate = jira.issue(jiraDict[issueName])
        issueToUpdate.update(fields={'description': issueDescription})
        print("Updating " + issueName + " : " + issueDescription)

if __name__ == "__main__":
    appendExistingTickets()
    readCSVReport()
    i = 0
    for vuln in listOfVulns:
        openNewIssues(listOfVulns[i], issuesDict[listOfVulns[i]])
        i = i + 1
    closeIssues()