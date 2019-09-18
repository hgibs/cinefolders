#!/bin/bash

# bump-publish.sh [major/minor/patch]
git add .
git commit

PART=$1
OLDVERSION=bump2version --dry-run --list $PART | grep current_version | awk '{split($0,a,"="); print "v"a[2]}'
NEWVERSION=bump2version --list $PART | grep new_version | awk '{split($0,a,"="); print "v"a[2]}'

git add .
git commit
git tag
git push --tags

python3 setup.py bdist_wheel sdist
twine upload -r pypi dist/*

rm -rf dist/*