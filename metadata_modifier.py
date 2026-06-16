#!/usr/bin/env python3
import sys
import os
import zipfile
import tempfile
import shutil
import subprocess
import time
import xml.etree.ElementTree as ET
from datetime import datetime

# Usage:
# python set_docx_metadata.py /path/to/file.docx --created "2026-05-01T12:00:00" --modified "2026-05-01T12:00:00" --lastmodifiedby "Name" --totaltime 42 --setfs

p = sys.argv[1] if len(sys.argv) > 1 else None
args = sys.argv[2:]

def parse_args(args):
    out = {}
    it = iter(args)
    for a in it:
        if a.startswith('--'):
            k = a[2:]
            v = next(it, None)
            out[k] = v
    return out

if not p:
    print("/Users/jerushawatson/Downloads/asia (1).docx")
    sys.exit(1)

opts = parse_args(args)

NS_DCTERMS = "http://purl.org/dc/terms/"
NS_CP = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
NS_XSI = "http://www.w3.org/2001/XMLSchema-instance"
NS_APP = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
ET.register_namespace('dcterms', NS_DCTERMS)
ET.register_namespace('cp', NS_CP)
ET.register_namespace('xsi', NS_XSI)
ET.register_namespace('', NS_APP)  # default for app.xml

def local_name(tag):
    return tag.split('}')[-1] if isinstance(tag, str) else tag

def upd_core_xml(b, created=None, modified=None, lastmodifiedby=None):
    root = ET.fromstring(b)
    changed = False
    # helper to find by local name
    def find_local(name):
        for el in root.iter():
            if local_name(el.tag).lower() == name.lower():
                return el
        return None
    if lastmodifiedby is not None:
        el = find_local('lastmodifiedby')
        if el is None:
            el = ET.SubElement(root, '{%s}lastmodifiedby' % NS_CP)
        el.text = lastmodifiedby
        changed = True
    if created is not None:
        el = find_local('created')
        if el is None:
            el = ET.SubElement(root, '{%s}created' % NS_DCTERMS)
        el.text = created
        # set xsi:type attribute as typical core.xml uses
        el.set('{%s}type' % NS_XSI, 'dcterms:W3CDTF')
        changed = True
    if modified is not None:
        el = find_local('modified')
        if el is None:
            el = ET.SubElement(root, '{%s}modified' % NS_DCTERMS)
        el.text = modified
        el.set('{%s}type' % NS_XSI, 'dcterms:W3CDTF')
        changed = True
    if not changed:
        return None
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)

def upd_app_xml(b, totaltime=None, pages=None, words=None, characters=None):
    root = ET.fromstring(b)
    changed = False
    def set_local(name, val, ns=NS_APP):
        nonlocal changed
        for el in root:
            if local_name(el.tag).lower() == name.lower():
                el.text = str(val)
                changed = True
                return
        e = ET.SubElement(root, '{%s}%s' % (ns, name))
        e.text = str(val)
        changed = True
    if totaltime is not None:
        set_local('TotalTime', totaltime)
    if pages is not None:
        set_local('Pages', pages)
    if words is not None:
        set_local('Words', words)
    if characters is not None:
        set_local('Characters', characters)
    if not changed:
        return None
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)

# read original zip, produce new zip in temp, replacing core/app if needed
tmp = tempfile.NamedTemporaryFile(delete=False)
tmp.close()
with zipfile.ZipFile(p, 'r') as zin, zipfile.ZipFile(tmp.name, 'w', zipfile.ZIP_DEFLATED) as zout:
    core_b = None
    app_b = None
    for name in zin.namelist():
        b = zin.read(name)
        if name == 'docProps/core.xml':
            core_b = b
        elif name == 'docProps/app.xml':
            app_b = b
        else:
            zout.writestr(name, b)
    # update core.xml
    new_core = None
    if core_b is not None:
        new_core = upd_core_xml(
            core_b,
            created=opts.get('created'),
            modified=opts.get('modified'),
            lastmodifiedby=opts.get('lastmodifiedby')
        )
    if new_core is None and core_b is not None:
        zout.writestr('docProps/core.xml', core_b)
    elif new_core is not None:
        zout.writestr('docProps/core.xml', new_core)
    # update app.xml
    new_app = None
    if app_b is not None:
        new_app = upd_app_xml(
            app_b,
            totaltime=opts.get('totaltime'),
            pages=opts.get('pages'),
            words=opts.get('words'),
            characters=opts.get('characters')
        )
    if new_app is None and app_b is not None:
        zout.writestr('docProps/app.xml', app_b)
    elif new_app is not None:
        zout.writestr('docProps/app.xml', new_app)

# replace original
shutil.move(tmp.name, p)

# optionally set filesystem times (mtime) and creation date on macOS
if 'modified' in opts and opts.get('setfs') is not None:
    # parse ISO-ish time
    try:
        dt = datetime.fromisoformat(opts['modified'].replace('Z','+00:00'))
    except Exception:
        dt = None
    if dt:
        ts = dt.timestamp()
        os.utime(p, (ts, ts))
if 'created' in opts and opts.get('setfs') is not None:
    # SetFile needed for macOS creation date change
    if shutil.which('SetFile'):
        subprocess.run(['SetFile', '-d', datetime.fromisoformat(opts['created'].replace('Z','+00:00')).strftime('%m/%d/%Y %H:%M:%S'), p])
    else:
        print("SetFile not found; install Xcode CLI tools (xcode-select --install) to change creation date.")

print("Done.")
