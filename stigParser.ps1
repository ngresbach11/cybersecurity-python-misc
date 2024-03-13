# DISA STIG scans can be automated in various ways, but you are always left with individual .ckl
# Files, and it can be a pain when you have thousands of those files to go through.
# The purpose of this is to help automate the process of parsing through DISA STIG checklists.
# This takes multiple files, and tracks which machines passed and failed given STIG checks.
# -------------------------------------
# To use, change file paths. Requires all .ckl files in same directory.
# Autodetects hostnames and adds all open findings to a CSV mapped to the hostname.
# You can easily use excel or grep to identify hosts with a given stig ID open

$input_directory = "\\Documents\Work\stigautomation\stigparser\sampleclk\" ## Change this value to the Directory you would like to run this script in. 
$output_path = "\\Documents\Work\stigautomation\stigparser\outputs" # Output filepath. Don't include file name or extension here.
$output_filename = "all_stig_results.csv"

$Allitems = Get-childitem -Path $input_directory -Filter *.ckl -Name
$Allobjects = @()

$hostVulnDict = @{}

foreach ($CKL in $Allitems) { # Iterate through each checklist. 

    write-host -Foregroundcolor Cyan "Working on $CKL..."

    [XML]$CKLdata = Get-Content $CKL # Convert file to XML object
    $hostname = $CKLData.Checklist.ASSET.HOST_NAME
    $foundOpens = New-Object System.Collections.ArrayList # Instantiate arraylist to store all open findings in
    $vulns = $CKLData.Checklist.STIGs.iSTIG.VULN # Grab each vulnerability from XML .ckl file and store in variable. We do this so we can access the 'Status' property to determine Open items.

    foreach ($vuln in $vulns) {
        $Newestvuln = $vuln ## Save the 'Open' items to a new variable name
        $Childnodes = $NewestVuln.ChildNodes  ## Declare child nodes variable, this picks up all of the child nodes to the individual vulnerability item ($Newestvuln)
        $Vuln_Num = $Childnodes.item(0).Attribute_Data

        if ($vuln.Status -eq "Open") {
            $foundOpens.Add($Vuln_Num) | out-null
         }
         Write-Host $Vuln_Num + " status : " + $vuln.Status + "  : "
     }
     $hostVulnDict[$hostname] = [string]($hostVulnDict[$hostname] + $foundOpens) # Maps all open findings to each hostname
}

$filedestination = $output_path + "\" + $output_filename
$hostVulnDict.GetEnumerator() | Select-Object -Property Key,Value | Export-CSV -NoTypeInformation -Path $filedestination