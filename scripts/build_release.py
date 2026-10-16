#!/usr/bin/env python3
"""Build 1.1.1 from verified base assets with the current SDDM repair overlaid."""
# SPDX-License-Identifier: MIT
import argparse, hashlib, json, shutil, subprocess, sys, tarfile, tempfile, urllib.request, zipfile
from pathlib import Path, PurePosixPath
VERSION='1.1.1'
BASE_SHA='9ac4f37cca0826a82c4cea7dbfd99766253decf0022d415ea2c1e06be922f34f'
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def overlay_sddm(archive, theme):
    """Replace only SDDM; retain all other file bytes and icon symlinks."""
    prefix='system/sddm/CrimsonGlass'
    with tempfile.TemporaryDirectory(dir=archive.parent) as temporary:
        replacement=Path(temporary)/'assets.tar.xz'
        with tarfile.open(archive,'r|xz') as source, tarfile.open(replacement,'w|xz') as output:
            for info in source:
                if info.name==prefix or info.name.startswith(prefix+'/'):continue
                output.addfile(info,source.extractfile(info) if info.isfile() else None)
            for path in sorted(theme.rglob('*')):
                if not path.is_file() or path.is_symlink():
                    if path.is_dir():continue
                    raise RuntimeError('Unexpected SDDM source type: '+str(path))
                info=output.gettarinfo(path,arcname=prefix+'/'+path.relative_to(theme).as_posix())
                info.uid=info.gid=info.mtime=0;info.uname=info.gname='';info.mode=0o644
                with path.open('rb') as content:output.addfile(info,content)
        replacement.replace(archive)
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
        theme=ROOT/'store/components/sddm/CrimsonGlass'
        shutil.copytree(theme,folder/'store/components/sddm/CrimsonGlass')
        overlay_sddm(folder/'assets.tar.xz',theme)
        sys.path.insert(0,str(ROOT));import dependencies
        (folder/'dependencies.json').write_text(json.dumps({'description':'Native prerequisites; see dependency recipes.','recipes':dependencies.RECIPES},indent=2)+'\n')
        inventory=json.loads((folder/'ASSET-INVENTORY.json').read_text());inventory['version']=VERSION
        counts={'regular_files':0,'symlinks':0,'directories':0,'uncompressed_file_bytes':0,'compressed_archive_bytes':(folder/'assets.tar.xz').stat().st_size}
        with tarfile.open(folder/'assets.tar.xz','r|xz') as assets:
            for item in assets:
                if item.isfile():counts['regular_files']+=1;counts['uncompressed_file_bytes']+=item.size
                elif item.issym():counts['symlinks']+=1
                elif item.isdir():counts['directories']+=1
        inventory['assets']=counts;(folder/'ASSET-INVENTORY.json').write_text(json.dumps(inventory,indent=2)+'\n')
        files=sorted(f for f in folder.rglob('*') if f.is_file() and '__pycache__' not in f.parts and f.name!='manifest.json')
        manifest={str(f.relative_to(folder)):sha(f) for f in files};(folder/'manifest.json').write_text(json.dumps({'format':1,'version':VERSION,'files':manifest},indent=2)+'\n')
        out=args.output/f'Crimson-Glass-{VERSION}.zip'
        with zipfile.ZipFile(out,'w') as z:
            for f in files+[folder/'manifest.json']:
                i=zipfile.ZipInfo(folder.name+'/'+str(f.relative_to(folder)),date_time=(2026,10,16,0,0,0));i.create_system=3;i.external_attr=((0o100755 if f.suffix=='.sh' else 0o100644)<<16);i.compress_type=zipfile.ZIP_STORED if f.name=='assets.tar.xz' else zipfile.ZIP_DEFLATED
                z.writestr(i,f.read_bytes(),compresslevel=6)
            assert z.testzip() is None
        out.with_suffix('.zip.sha256').write_text(sha(out)+'  '+out.name+'\n')
        r=subprocess.run([sys.executable,folder/'install.py','--dry-run','--home',temp/'home','--offline','--skip-deps','--no-layout'],text=True,capture_output=True)
        if r.returncode:raise RuntimeError(r.stdout+r.stderr)
        print(json.dumps({'zip':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'files':len(manifest)+1,'dry_run':'passed'},indent=2))
if __name__=='__main__':main()
