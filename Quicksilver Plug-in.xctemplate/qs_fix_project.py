#!/usr/bin/env python

import os
import sys
import shutil
import re

target_file = ''
project_name = ''

## locate the project file
for f in os.listdir('.'):
    if f.endswith('.xcodeproj'):
        target_file = f + '/project.pbxproj'
        project_name = f[:-10]

if not os.path.exists(target_file):
    print "Project file not found. Run this from the directory it's in."
    sys.exit(1)

## get project and target identifiers
processing = False
project = False
target = False
idpat = re.compile(r'\s+([0-9A-Z]{24}) /\* (\w+) \*/')
rproj = 'INVALIDINVALIDINVALID'
dproj = 'INVALIDINVALIDINVALID'
rtarg = 'INVALIDINVALIDINVALID'
dtarg = 'INVALIDINVALIDINVALID'
for line in open(target_file):
    if 'Begin XCConfigurationList section' in line:
        processing = True
        continue
    if not processing:
        continue
    if 'End XCConfigurationList section' in line:
        processing = False
        continue
    if 'PBXProject' in line:
        project = True
        continue
    if 'PBXNativeTarget' in line:
        target = True
        continue
    m = idpat.match(line)
    if project:
        if '};' in line:
            ## done with the project section
            project = False
            continue
        if m:
            if m.group(2) == 'Release':
                rproj = m.group(1)
            else:
                dproj = m.group(1)
    if target:
        if '};' in line:
            ## done with the project section
            project = False
            continue
        if m:
            if m.group(2) == 'Release':
                rtarg = m.group(1)
            else:
                dtarg = m.group(1)

## clean up the project
conf = re.compile(r'\s+path = .*private/tmp/QS/Configuration;')
pconf = re.compile(r'\s+([0-9A-Z]{24} /\* QSPlugIn\.xcconfig \*/) = {isa = PBXFileReference')
dconf = re.compile(r'\s+([0-9A-Z]{24} /\* Debug\.xcconfig \*/) = {isa = PBXFileReference')
rconf = re.compile(r'\s+([0-9A-Z]{24} /\* Release\.xcconfig \*/) = {isa = PBXFileReference')
plistpat = re.compile(r'\w+-Info\.plist')
pxcid = 'INVALIDINVALIDINVALID'
dxcid = 'INVALIDINVALIDINVALID'
rxcid = 'INVALIDINVALIDINVALID'
debug_proj = False
debug_targ = False
release_proj = False
release_targ = False
new_contents = []
cleaning = False
for line in open(target_file):
    ## are we in the middle of cleaning something?
    if cleaning:
        ## end of the section, stop cleaning
        if '};' in line:
            cleaning = False
        elif 'PRODUCT_NAME' not in line:
            ## remove lines except for Product Name
            continue
    ## remove references to scripts
    if '/* bltrversion */' in line or 'qs_fix_project.py' in line:
        continue
    ## are we about to need an xcconfig file?
    if rproj in line:
        release_proj = True
    if dproj in line:
        debug_proj = True
    if rtarg in line:
        release_targ = True
    if dtarg in line:
        debug_targ = True
    ## clean out build settings and add xcconfig
    if 'buildSettings = {' in line:
        cleaning = True
        if release_proj:
            xc = rxcid
            release_proj = False
        if debug_proj:
            xc = dxcid
            debug_proj = False
        if release_targ:
            xc = pxcid
            release_targ = False
        if debug_targ:
            xc = pxcid
            debug_targ = False
        new_contents.append('\t\t\tbaseConfigurationReference = %s;\n' % xc)
    else:
        ## make the last xcconfig file refer to the file and not the parent folder
        if 'lastKnownFileType = folder; name = Release.xcconfig; path = /tmp/QS/Configuration' in line:
            line = line.replace('folder', 'text.xcconfig')
            line = line.replace('/tmp/QS/Configuration', 'Release.xcconfig')
            line = line.replace('<absolute>', '<group>')
            line = line.replace('name = Release.xcconfig; ', '')
        ## don't add Release.xcconfig to the target
        if line.endswith('/* Release.xcconfig in Resources */,\n'):
            continue
        ## make the absolute path actually absolute
        if conf.match(line):
            line = re.sub(r' = .*private', ' = ', line)
    ## store xcconfig identifiers for later
    m = pconf.match(line)
    if m:
        pxcid = m.group(1)
    m = dconf.match(line)
    if m:
        dxcid = m.group(1)
    m = rconf.match(line)
    if m:
        rxcid = m.group(1)
    m = plistpat.match(line)
    ## fix references to the plist
    line = re.sub(plistpat, 'Info.plist', line)
    if 'Info.plist */ = {isa = PBXFileReference' in line:
        line = line.replace('"<group>"', 'SOURCE_ROOT')
    ## keep this line
    new_contents.append(line)

## write the new file
replacement = open(target_file, 'w')
replacement.writelines(new_contents)
replacement.close()

## rename Info.plist
oldplist = '%s/%s-Info.plist' % (project_name, project_name)
newplist = 'Info.plist'
shutil.move(oldplist, newplist)
## remove this script
os.remove(sys.argv[0])
