param (
	[Parameter( Mandatory = $True )]
	[string]$Thumbprint
)

.\build.ps1 -Thumbprint $Thumbprint -CabName 'Z-Atlas-NoDefender-Package31bf3856ad364e35amd643.0.0.0.cab'

Write-Output "Deleting temp folder..."
Remove-Item -Path 'C:\Users\he3als\AppData\Local\Temp\tmpi0ytoowp' -Force -Recurse
