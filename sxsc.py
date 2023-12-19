import yaml, havesxs, uuid, hashlib, base64, os, tempfile

# FXEFqZQLNdyPGADgoUdluRUTzVkGUI/H7FOiuNUDjuk=
PUBLIC_KEY_TOKEN = "31bf3856ad364e35"
tempDir = None

# """"update"""", a term microsoft uses to describe literally 50 million things
class Update:
    def __init__(
        self,
        target_component,
        target_arch,
        version,
        copyright,
        registry_keys=None,
        files=None,
        version_scope="nonSxS",
        standalone="yes"
    ):
        self.identifier = hashlib.sha1(str(uuid.uuid4()).encode('ascii')).hexdigest()
        self.target_component = target_component
        self.target_arch = target_arch
        self.version = version
        self.copyright = copyright
        self.registry_keys = registry_keys
        self.files = files
        self.version_scope = version_scope
        self.public_key_token = PUBLIC_KEY_TOKEN
        self.standalone = standalone

    def generate_component_sxs(self):
        return havesxs.generate_sxs_name(
            {
                "name": self.target_component,
                "culture": "none",
                "version": self.version,
                "publicKeyToken": self.public_key_token,
                "processorArchitecture": self.target_arch,
                "versionScope": self.version_scope,
            }
        )

    def generate_component_manifest(self):
        global tempDir

        registry_entries = []
        if self.registry_keys:
            for registry_key in self.registry_keys:
                registry_values = []
                for registry_value in registry_key['values']:
                    registry_values.append(f"""<registryValue name="{registry_value['key']}" valueType="{registry_value['type']}" value="{registry_value['value']}" />""")
                registry_values = '\n'.join(registry_values)
                registry_entries.append(f"""<registryKey keyName="{registry_key['key_name']}" perUserVirtualization="{'Enable' if registry_key['perUserVirtualization'] else 'Disable'}">{registry_values}</registryKey>""")

        files_list = []
        files_entries = []
        if self.files:
            for file in self.files:
                if file.get('operation') == 'delete':
                    if tempDir == None:
                        tempDir = tempfile.mkdtemp()
                    
                    deletedFile = os.path.join(tempDir, file['file'])
                    with open(deletedFile, 'wb') as f:
                        f.write(b'\x01')  # write a 1 bit, needed for makecat
                    
                    filePath = deletedFile
                else:
                    filePath = file['file']

                try: 
                    with open(filePath, 'rb') as f:
                        dsig = base64.b64encode(hashlib.sha256(f.read()).digest()).decode()

                    files_entries.append(f"""<file name="{filePath}" destinationPath="{file['destination']}" importPath="$(build.nttree)\\"><asmv2:hash xmlns:asmv2="urn:schemas-microsoft-com:asm.v2" xmlns:dsig="http://www.w3.org/2000/09/xmldsig#"><dsig:Transforms><dsig:Transform Algorithm="urn:schemas-microsoft-com:HashTransforms.Identity" /></dsig:Transforms><dsig:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha256" /><dsig:DigestValue>{dsig}</dsig:DigestValue></asmv2:hash></file>""")
                    files_list.append(filePath)
                except FileNotFoundError:
                    print(f"{file['file']} specified not found.")

        registry_entries = "<registryKeys>" + "".join(registry_entries) + "</registryKeys>" if registry_entries else ""
        files_entries = "".join(files_entries) if files_entries else ""
        return [
            f"""<?xml version="1.0" encoding="utf-8" standalone="{self.standalone}"?><assembly xmlns="urn:schemas-microsoft-com:asm.v3" manifestVersion="1.0" copyright="{self.copyright}"><assemblyIdentity name="{self.target_component}" version="{self.version}" processorArchitecture="{self.target_arch}" language="neutral" buildType="release" publicKeyToken="{self.public_key_token}" versionScope="{self.version_scope}" />{registry_entries}{files_entries}</assembly>""",
            files_list
        ]

    def generate_update_sxs(self, culture = "none"):
        return havesxs.generate_sxs_name(
            {
                "name": self.identifier,
                "culture": culture,
                "version": self.version,
                "publicKeyToken": self.public_key_token,
                "processorArchitecture": self.target_arch,
                "versionScope": self.version_scope,
            }
        )

    def generate_update_manifest(self, discoverable = False):
        return f"""<?xml version="1.0" encoding="utf-8" standalone="{self.standalone}"?><assembly xmlns="urn:schemas-microsoft-com:asm.v3" manifestVersion="1.0" copyright="{self.copyright}"><assemblyIdentity name="{self.identifier}" version="{self.version}" processorArchitecture="{self.target_arch}" language="neutral" buildType="release" publicKeyToken="{self.public_key_token}" versionScope="{self.version_scope}"/><deployment xmlns="urn:schemas-microsoft-com:asm.v3"/><dependency discoverable=\"{"true" if discoverable else "false"}\"><dependentAssembly dependencyType="install"><assemblyIdentity name="{self.target_component}" version="{self.version}" processorArchitecture="{self.target_arch}" language="neutral" buildType="release" publicKeyToken="{self.public_key_token}" versionScope="{self.version_scope}"/></dependentAssembly></dependency></assembly>"""


# Package Definition
class MicrosoftUpdateManifest:
    def __init__(self, package, copyright, version, target_arch, updates):
        self.package = package
        self.copyright = copyright
        self.version = version
        self.target_arch = target_arch
        self.public_key_token = PUBLIC_KEY_TOKEN
        self.updates = updates

    def generate_mum(self):
        mum = f"""<?xml version="1.0" encoding="utf-8" standalone="yes"?><assembly xmlns="urn:schemas-microsoft-com:asm.v3" manifestVersion="1.0" copyright="{self.copyright}"><assemblyIdentity name="{self.package}" version="{self.version}" processorArchitecture="{self.target_arch}" language="neutral" buildType="release" publicKeyToken="{self.public_key_token}"/><package identifier="{self.package}" releaseType="Feature Pack">"""
        mum += "".join(list(map(self.generate_mum_update, self.updates)))
        mum += "</package></assembly>"
        return mum

    def generate_mum_update(self, update):
        return f"""<update name="{update.identifier}"><component><assemblyIdentity name="{update.identifier}" version="{update.version}" processorArchitecture="{update.target_arch}" language="neutral" buildType="release" publicKeyToken="{update.public_key_token}" versionScope="{update.version_scope}"/></component></update>"""


with open("cfg.yaml", "r") as f:
    config = yaml.safe_load(f)

# Staging Arena
staged_updates = []
staged_ddf = ["update.mum", "update.cat"]
staged_files = ["update.mum", "update.cat"]

for update in config["updates"] or []:
    update = Update(**update, copyright=config["copyright"])
    component_sxs = update.generate_component_sxs()
    update_sxs = update.generate_update_sxs()
    files = [f"{component_sxs}.manifest", f"{update_sxs}.manifest"] 

    with open(f".\\{component_sxs}.manifest", "w+") as f:
        component_manifest = update.generate_component_manifest()

        if component_manifest[1] != []:
            for file in component_manifest[1]:
                staged_ddf.append(f".Set DestinationDir={component_sxs}")
                staged_ddf.append(file)
                staged_files.append(file)

            staged_ddf.append(f".Set DestinationDir=")
        
        f.write(component_manifest[0])
    with open(f".\\{update_sxs}.manifest", "w+") as f:
        f.write(update.generate_update_manifest())
    staged_updates.append(update)
    staged_ddf.extend(files)
    staged_files.extend(files)

with open(".\\update.mum", "w+") as f:
    f.write(
        MicrosoftUpdateManifest(
            config["package"],
            config["copyright"],
            config["version"],
            config["target_arch"],
            staged_updates,
        ).generate_mum()
    )

with open(".\\files.txt", "w+") as f:
    f.write("\n".join(staged_ddf))

with open(".\\update.cdf", "w+") as f:
    f.write("""[CatalogHeader]
Name=update.cat
ResultDir=.\\
CatalogVersion=2
HashAlgorithms=SHA256

[CatalogFiles]
""")
    for (i, filename) in enumerate(filter(lambda f: f != "update.cat", staged_files)):
        f.write(f"<HASH>F{i+1}={filename}\n")

with open(".\\build.bat", "w+") as f:
    f.write(f"""@echo off
echo Setting the variables...
set CAB_NAME={config['package']}{PUBLIC_KEY_TOKEN}{config['target_arch']}{config['version']}.cab
set "root=%PROGRAMFILES(X86)%\\Windows Kits\\10\\bin"
for /f %%a in ('dir /b /o:n "%root%" ^| find "0"') do set "path1=%root%\\%%a\\x64"
set "PATH=%PATH%;%path1%"

echo Making CAT...
makecat update.cdf > nul || exit /b 1
echo Signing CAT...
signtool.exe sign /f sxs.pfx /p 1 /fd SHA256 update.cat  > nul || exit /b 1

echo Making CAB...
makecab /d "CabinetName1=%CAB_NAME%" /f files.txt > nul || exit /b 1
del /f setup.* > nul 2>&1
echo Signing CAB...
signtool sign /f sxs.pfx /p 1 /fd SHA256 disk1\\%CAB_NAME% > nul || exit /b 1

echo Copying CAB to main directory...
copy disk1\\*.cab . > nul""")

if not tempDir == None:
    with open(".\\build.bat", 'a') as f:
        f.write(f"""\n
echo Deleting temp folder...
rmdir /s /q "{tempDir}" > nul
""")