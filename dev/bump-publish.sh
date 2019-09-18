#!/bin/bash

if [ -z "$*" ]; then
    echo 'Usage: dev/bump-publish.sh [major/minor/patch]'
    exit 1
fi

PART=$1

# dev/bump-publish.sh [major/minor/patch]
git add .
git commit

PART=$1
OLDVERSION="$(bump2version --dry-run --list $PART | grep current_version | awk '{split($0,a,"="); print "v"a[2]}' )"
NEWVERSION="$(bump2version --dry-run --list $PART | grep new_version | awk '{split($0,a,"="); print "v"a[2]}' )"

bump2version $PART

echo -e "\n\n$OLDVERSION → $NEWVERSION" > dev/git-template.txt

nano dev/git-template.txt

git add .
git commit -F dev/git-template.txt
git tag -a $NEWVERSION -F dev/git-template.txt
git push --tags

python3 setup.py bdist_wheel sdist
twine upload -r pypi dist/*

rm -rf dist/*