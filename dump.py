# Copyright (C) 2023  echnobas

import xml.etree.ElementTree
from havesxs import generate_sxs_name
import hashlib, random, shutil, os

CONFIG = {
    "PACKAGE_NAME": "Echnobas-NoTelem-Package",
    "PACKAGE_VER": "1.0.0.0",
    "PACKAGE_ARCH": "amd64",
    "COPYRIGHT": "(c) Echnobas",
    "COMPONENT_VER": "420.69.0.0",
    "COMPONENT_LIST": ".\\telem.xml",

    "PUBLIC_KEY_TOKEN": "31bf3856ad364e35",
}

def generate_hash():
    return hashlib.sha1(random.randbytes(24)).hexdigest()

def parse_assembly_identity(xml_string):
    root = xml.etree.ElementTree.fromstring(xml_string)
    fields = {}
    for attr, value in root.attrib.items():
        fields[attr] = value
    return fields

def create_component_manifest(data):
    return f"""<?xml version="1.0" encoding="utf-8" standalone="yes"?><assembly xmlns="urn:schemas-microsoft-com:asm.v3" manifestVersion="1.0" copyright="{CONFIG['COPYRIGHT']}"><assemblyIdentity name="{parsed['name']}" version="{data['version']}" processorArchitecture="{data['processorArchitecture']}" language="neutral" buildType="release" publicKeyToken="{data['publicKeyToken']}" versionScope="{data['versionScope']}" /></assembly>"""

def create_update_manifest(update_id, component_name, data):
    return f"""<?xml version="1.0" encoding="utf-8" standalone="yes"?><assembly xmlns="urn:schemas-microsoft-com:asm.v3" manifestVersion="1.0" copyright="{CONFIG['COPYRIGHT']}"><assemblyIdentity name="{update_id}" version="{data['version']}" processorArchitecture="{data['processorArchitecture']}" language="neutral" buildType="release" publicKeyToken="{CONFIG['PUBLIC_KEY_TOKEN']}" versionScope="{data['versionScope']}" /><deployment xmlns="urn:schemas-microsoft-com:asm.v3" /><dependency discoverable="false"><dependentAssembly dependencyType="install"><assemblyIdentity name="{component_name}" version="{data['version']}" processorArchitecture="{data['processorArchitecture']}" language="neutral" buildType="release" publicKeyToken="{CONFIG['PUBLIC_KEY_TOKEN']}" versionScope="{data['versionScope']}" /></dependentAssembly></dependency></assembly>"""

def create_mum_component_manifest(update_id, data):
    return f"""<update name="{update_id}"><component><assemblyIdentity name="{update_id}" version="{data['version']}" processorArchitecture="{data['processorArchitecture']}" language="neutral" buildType="release" publicKeyToken="{data['publicKeyToken']}" versionScope="{data['versionScope']}" /></component></update>"""

mum = open("update.mum", "w+")
cat = open("update.cdf", "w+")
files = open("files.txt", "w+")
filenumber = 2
done = []

try:
    print("Cleaning..")
    shutil.rmtree('.\\dump')
except:
    print("Working tree clean, not cleaning..")
os.mkdir(".\\dump")

mum.write(f"""<?xml version="1.0" encoding="utf-8" standalone="yes"?><assembly xmlns="urn:schemas-microsoft-com:asm.v3" manifestVersion="1.0" copyright="{CONFIG['COPYRIGHT']}"><assemblyIdentity name="{CONFIG['PACKAGE_NAME']}" version="{CONFIG['PACKAGE_VER']}" processorArchitecture="{CONFIG['PACKAGE_ARCH']}" language="neutral" buildType="release" publicKeyToken="{CONFIG['PUBLIC_KEY_TOKEN']}" /><package identifier="{CONFIG['PACKAGE_NAME']}" releaseType="Feature Pack">""")
cat.write("""[CatalogHeader]
Name=update.cat
ResultDir=.\\
CatalogVersion=2
HashAlgorithms=SHA256

[CatalogFiles]
<HASH>F1=.\\update.mum\n""")
files.write("update.mum\nupdate.cat\n")

with open(CONFIG["COMPONENT_LIST"], "r") as f:
    for i, line in enumerate(f.readlines()):
        parsed = parse_assembly_identity(line)
        print(f"Loading {parsed['name']}_{parsed['processorArchitecture']}", end="")
        if (parsed['name'], parsed['processorArchitecture']) in done:
            print(" ... duplicate")
            continue
        else: print()
        
        try:
            data = {
                "name": parsed["name"],
                "culture": "none",
                "version": CONFIG["COMPONENT_VER"],
                "publicKeyToken": parsed["publicKeyToken"],
                "processorArchitecture": parsed["processorArchitecture"],
                "versionScope": parsed["versionScope"]
            }
            done.append((parsed['name'], parsed['processorArchitecture']))
        except KeyError:
            continue

        component_generated_sxs_name = generate_sxs_name(data)
        component_generated_manifest = create_component_manifest(data)
        with open(f"dump\\{component_generated_sxs_name}.manifest", "w+") as f:
            f.write(component_generated_manifest)

        update_id = generate_hash()
        data['name'] = update_id
        update_generated_sxs_name = generate_sxs_name(data)
        update_generated_manifest = create_update_manifest(update_id, parsed['name'], data)
        with open(f"dump\\{update_generated_sxs_name}.manifest", "w+") as f:
            f.write(update_generated_manifest)
        files.write(f"dump\\{component_generated_sxs_name}.manifest\ndump\\{update_generated_sxs_name}.manifest\n")
        cat.write(f"<HASH>F{filenumber}=.\dump\{component_generated_sxs_name}.manifest\n")
        cat.write(f"<HASH>F{filenumber + 1}=.\dump\{update_generated_sxs_name}.manifest\n")
        
        mum_generated_manifest = create_mum_component_manifest(update_id, data)
        mum.write(mum_generated_manifest)
        filenumber += 2

mum.write("</package></assembly>")
mum.close()
cat.close()
files.close()

with open("build.bat", "w+") as f:
    f.write(f"""@echo off
set CAB_NAME={CONFIG['PACKAGE_NAME']}{CONFIG['PUBLIC_KEY_TOKEN']}{CONFIG['PACKAGE_ARCH']}{CONFIG['PACKAGE_VER']}.cab

del /f update.cat 2>NUL
del /f *.cab 2>NUL
bin\makecat update.cdf || exit /b 1
bin\signtool.exe sign /f sxs.pfx /p 1 /fd SHA256 update.cat || exit /b 1
bin\makecab /d "CabinetName1=%CAB_NAME%" /f files.txt || exit /b 1
del /f setup.* 2>NUL
bin\signtool.exe sign /f sxs.pfx /p 1 /fd SHA256 disk1\%CAB_NAME% || exit /b 1
copy disk1\*.cab . >NUL""")