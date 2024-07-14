$store = 'Cert:\LocalMachine\My'
$params = @{
	Type = 'Custom'
	Subject = 'CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US'
	TextExtension = @(
		# Enhanced Key Usage
		'2.5.29.37={text}1.3.6.1.4.1.311.10.3.6',
		# Basic Constraints
		'2.5.29.19={text}false',
		# Subject Alternative Name
		'2.5.29.17={text}DirectoryName=SERIALNUMBER="229879+500176",OU=Microsoft Ireland Operations Limited'
	)
	KeyUsage = 'None'
	KeyAlgorithm = 'RSA'
	KeyLength = 2048
	NotAfter = (Get-Date).AddMonths(9999)
	CertStoreLocation = $store
}
(New-SelfSignedCertificate @params).Thumbprint

# $path = "$store\$((New-SelfSignedCertificate @params).Thumbprint)"
# Export-PfxCertificate -Cert $path -FilePath "sxs.pfx" -Password '1' -NoProperties
# Get-ChildItem $path | Remove-Item -Force