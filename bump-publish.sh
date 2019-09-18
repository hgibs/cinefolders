#!/bin/bash

# bump-publish.sh [major/minor/patch]
git add .
git commit

PART=$1
bump2version $PART 

python3 setup.py bdist_wheel sdist
twine upload -r pypi dist/*