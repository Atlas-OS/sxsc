param (
    [string]$Thumbprint,
    [string]$CabName
)

Write-Output "Setting the variables..."
$bin = Test-Path "bin"
$winKit = Get-ChildItem -Path "$([Environment]::GetFolderPath('ProgramFilesx86'))\Windows Kits\10\bin" -Directory -Filter '*.0*' |
    Sort-Object -Descending |
    Select-Object -First 1
if (($winKit.Count -eq 0) -and !$bin) { throw "Windows Kit not found!" }
$env:PATH += ";$winKit"
if ($bin) { $env:path += ";$PWD\bin" }

Write-Output "Making CAT..."
$cat = makecat update.cdf
if ($LASTEXITCODE -ne 0) { throw "Failed to make CAT! $cat" }

Write-Output "Signing CAT..."
$cat1 = signtool sign /sm /uw /sha1 $Thumbprint /fd SHA256 update.cat
if ($LASTEXITCODE -ne 0) { throw "Failed to sign CAT! $cat1" }

Write-Output "Making CAB..."
$cab = makecab /d "CabinetName1=$cabName" /f files.txt
if ($LASTEXITCODE -ne 0) { throw "Failed to make CAB! $cab" }
Remove-Item -Path "setup.*" -Force -EA 0

Write-Output "Signing CAB..."
$cab1 = signtool sign /sm /uw /sha1 $Thumbprint /fd SHA256 "disk1\$cabName"
if ($LASTEXITCODE -ne 0) { throw "Failed to sign CAB! $cab1" }

Write-Output "Copying CAB to main directory..."
Copy-Item -Path "disk1\*.cab" -Destination "." -Force