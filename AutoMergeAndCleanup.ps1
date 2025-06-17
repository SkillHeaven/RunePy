# Script to merge a pull request branch into main and delete the branch
param(
    [Parameter(Mandatory=$true)]
    [string]$BranchName,
    [string]$Remote = "origin",
    [string]$MainBranch = "main"
)

Write-Host "Checking out main branch: $MainBranch"
& git checkout $MainBranch
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Pulling latest changes from $Remote/$MainBranch"
& git pull $Remote $MainBranch
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Merging branch '$BranchName'"
& git merge --no-ff $BranchName -m "Merge branch '$BranchName'"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Pushing merge to $Remote"
& git push $Remote $MainBranch
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Deleting remote branch $BranchName"
& git push $Remote --delete $BranchName

Write-Host "Deleting local branch $BranchName"
& git branch -d $BranchName
