#!/usr/bin/env python3
"""Build 1.1.0 using the unchanged, checksum-verified 1.0.0 visual payload."""
# SPDX-License-Identifier: MIT
import argparse, hashlib, json, shutil, subprocess, sys, tempfile, urllib.request, zipfile
from pathlib import Path, PurePosixPath
VERSION='1.1.0'
BASE_SHA='9ac4f37cca0826a82c4cea7dbfd99766253decf0022d415ea2c1e06be922f34f'
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base-zip',type=Path);p.add_argument('--output',type=Path,default=ROOT/'dist');args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as t:
        temp=Path(t);base=args.base_zip
        if base is None:
            base=temp/'base.zip';urllib.request.urlretrieve('https://github.com/SirFork1988/Crimson-Glass/releases/download/v1.0.0/Crimson-Glass-1.0.0.zip',base)
        if sha(base)!=BASE_SHA:raise RuntimeError('Base release checksum does not match the published 1.0.0 package')
        folder=temp/f'Crimson-Glass-{VERSION}';folder.mkdir()
        with zipfile.ZipFile(base) as z:
            for info in z.infolist():
                parts=PurePosixPath(info.filename).parts
                if not parts or parts[0]!='Crimson-Glass-1.0.0' or '..' in parts:raise RuntimeError('Unsafe base ZIP path')
                rel=Path(*parts[1:])
                if not parts[1:] or info.is_dir():continue
                dest=folder/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(z.read(info))
        for name in ('install.py','install.sh','restore.sh','startup.py','dependencies.py','settings.json','layout.js','runtime_install.py','README.md','README.txt','CREDITS.txt','LICENSE','VALIDATION.txt','RELEASE-NOTES.md'):
            shutil.copy2(ROOT/name,folder/name)
        for name in ('runtime','tests','scripts','licenses','screenshots'):
            shutil.copytree(ROOT/name,folder/name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        sys.path.insert(0,str(ROOT));import dependencies
        (folder/'dependencies.json').write_text(json.dumps({'description':'Native prerequisites; see dependency recipes.','recipes':dependencies.RECIPES},indent=2)+'\n')
        inventory=json.loads((folder/'ASSET-INVENTORY.json').read_text());inventory['version']=VERSION;(folder/'ASSET-INVENTORY.json').write_text(json.dumps(inventory,indent=2)+'\n')
        files=sorted(f for f in folder.rglob('*') if f.is_file() and '__pycache__' not in f.parts and f.name!='manifest.json')
        manifest={str(f.relative_to(folder)):sha(f) for f in files};(folder/'manifest.json').write_text(json.dumps({'format':1,'version':VERSION,'files':manifest},indent=2)+'\n')
        out=args.output/f'Crimson-Glass-{VERSION}.zip'
        with zipfile.ZipFile(out,'w') as z:
            for f in files+[folder/'manifest.json']:
                i=zipfile.ZipInfo(folder.name+'/'+str(f.relative_to(folder)),date_time=(2026,10,9,0,0,0));i.create_system=3;i.external_attr=((0o100755 if f.suffix=='.sh' else 0o100644)<<16);i.compress_type=zipfile.ZIP_STORED if f.name=='assets.tar.xz' else zipfile.ZIP_DEFLATED
                z.writestr(i,f.read_bytes(),compresslevel=6)
            assert z.testzip() is None
        out.with_suffix('.zip.sha256').write_text(sha(out)+'  '+out.name+'\n')
        r=subprocess.run([sys.executable,folder/'install.py','--dry-run','--home',temp/'home','--offline','--skip-deps','--no-layout'],text=True,capture_output=True)
        if r.returncode:raise RuntimeError(r.stdout+r.stderr)
        print(json.dumps({'zip':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'files':len(manifest)+1,'dry_run':'passed'},indent=2))
if __name__=='__main__':main()
