@(
	"build.bat",
	"files.txt",
	"*.manifest",
	"update*",
	".\disk1\*",
	".\disk1",
	"*.cab"
) | ForEach-Object { Remove-Item -Path $_ -Recurse -Force -EA 0 }