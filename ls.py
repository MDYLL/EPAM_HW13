import argparse
import os
import pathlib
import logging

logging.basicConfig(level=logging.DEBUG,filename='ls.log',filemode='w')
logger=logging.getLogger()

parser = argparse.ArgumentParser()
parser.add_argument('mask', nargs='?', default='*',help='mask of files')
parser.add_argument('-r', action='store_true',help='reversed output')
parser.add_argument('-a', action='store_false',help='show hidden files')


args = parser.parse_args()
path = '.'

if os.path.isdir(args.mask):
    path = os.path.join(path, args.mask)
    mask = '*'
elif '/' in args.mask:
    folders = args.mask.split('/')
    for folder in folders[:-1]:
        path = os.path.join(path, folder)
    mask = folders[-1]
else:
    mask = args.mask
logger.debug(f"path={path}, mask={mask}")
file_refs = pathlib.Path(path).glob(mask)
files = []
for file in file_refs:
    if os.path.isdir(file):
        files.append(str(file)[len(path) - 1:] + '/')
    else:
        files.append(str(file)[len(path) - 1:])
if args.r:
    files = reversed(files)
if args.a:
    tmp_files = []
    for file_ in files:
        if file_[0] != '.':
            tmp_files.append(file_)
    files = tmp_files

print('\t'.join(files))
