param (
	[string]$Thumbprint
)

if ($Thumbprint) {
	Get-ChildItem "Cert:\LocalMachine\My\$Thumbprint" | Remove-Item
	exit
}

@(
	"build.bat",
	"files.txt",
	"*.manifest",
	"update*",
	".\disk1\*",
	".\disk1",
	"*.cab"
) | ForEach-Object { Remove-Item -Path $_ -Recurse -Force -EA 0 }