# -*- coding: utf-8 -*-

# Resource object code
#
# Created by: The Resource Compiler for PyQt5 (Qt v5.15.2)
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore

qt_resource_data = b"\
\x00\x00\x01\x14\
\x3c\
\x73\x76\x67\x20\x78\x6d\x6c\x6e\x73\x3d\x22\x68\x74\x74\x70\x3a\
\x2f\x2f\x77\x77\x77\x2e\x77\x33\x2e\x6f\x72\x67\x2f\x32\x30\x30\
\x30\x2f\x73\x76\x67\x22\x20\x77\x69\x64\x74\x68\x3d\x22\x32\x34\
\x22\x20\x68\x65\x69\x67\x68\x74\x3d\x22\x32\x34\x22\x20\x76\x69\
\x65\x77\x42\x6f\x78\x3d\x22\x30\x20\x30\x20\x32\x34\x20\x32\x34\
\x22\x20\x66\x69\x6c\x6c\x3d\x22\x6e\x6f\x6e\x65\x22\x20\x73\x74\
\x72\x6f\x6b\x65\x3d\x22\x23\x66\x35\x34\x32\x34\x32\x22\x20\x73\
\x74\x72\x6f\x6b\x65\x2d\x77\x69\x64\x74\x68\x3d\x22\x32\x22\x20\
\x73\x74\x72\x6f\x6b\x65\x2d\x6c\x69\x6e\x65\x63\x61\x70\x3d\x22\
\x72\x6f\x75\x6e\x64\x22\x20\x73\x74\x72\x6f\x6b\x65\x2d\x6c\x69\
\x6e\x65\x6a\x6f\x69\x6e\x3d\x22\x72\x6f\x75\x6e\x64\x22\x3e\x0a\
\x20\x20\x3c\x6c\x69\x6e\x65\x20\x78\x31\x3d\x22\x31\x38\x22\x20\
\x79\x31\x3d\x22\x36\x22\x20\x78\x32\x3d\x22\x36\x22\x20\x79\x32\
\x3d\x22\x31\x38\x22\x3e\x3c\x2f\x6c\x69\x6e\x65\x3e\x0a\x20\x20\
\x3c\x6c\x69\x6e\x65\x20\x78\x31\x3d\x22\x36\x22\x20\x79\x31\x3d\
\x22\x36\x22\x20\x78\x32\x3d\x22\x31\x38\x22\x20\x79\x32\x3d\x22\
\x31\x38\x22\x3e\x3c\x2f\x6c\x69\x6e\x65\x3e\x0a\x0a\x3c\x2f\x73\
\x76\x67\x3e\
"

qt_resource_name = b"\
\x00\x08\
\x00\xb2\xb7\xe2\
\x00\x74\
\x00\x69\x00\x74\x00\x6c\x00\x65\x00\x62\x00\x61\x00\x72\
\x00\x05\
\x00\x7b\x5a\xc7\
\x00\x78\
\x00\x2e\x00\x73\x00\x76\x00\x67\
"

qt_resource_struct_v1 = b"\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x01\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x02\
\x00\x00\x00\x16\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\
"

qt_resource_struct_v2 = b"\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x01\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x02\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x16\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\
\x00\x00\x01\x86\x73\x1e\x33\x26\
"

qt_version = [int(v) for v in QtCore.qVersion().split('.')]
if qt_version < [5, 8, 0]:
    rcc_version = 1
    qt_resource_struct = qt_resource_struct_v1
else:
    rcc_version = 2
    qt_resource_struct = qt_resource_struct_v2

def qInitResources():
    QtCore.qRegisterResourceData(rcc_version, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(rcc_version, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()