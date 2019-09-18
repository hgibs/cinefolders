#!/bin/bash

# bump-publish.sh [major/minor/patch]
git add .
git commit

PART=$1
bump2version $PART | grep new_version | awk '{split($0,a,"="); print a[1]}'

git commit
git tag
git push --tags

python3 setup.py bdist_wheel sdist
twine upload -r pypi dist/*

rm -rf dist/*