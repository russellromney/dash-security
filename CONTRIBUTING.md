# Contributing to dash-security

Contributions to Dash Security are welcome! Steps to contribute: 
* clone the repo (or fork the repo and clone your fork)
* create a feature branch with a helpful name like `contrib/add-somefeature`
* commit change to your local branch
* push those commits to your branch (or to your fork branch)
* open a Pull Request on this repo with your changes


This project uses Poetry to manage dependencies, and includes a `requirements.txt` for dev as well as for the example to make it easy for users or developers to choose how to manage Python dependencies. 

```shell
# install poetry
pip install poetry 
# OR on Mac; 
brew install poetry

# create a virtual env and install specified dependencies
poetry install 

# add a new dependency
poetry add packagename

# export updated requirements to update requirements.txt
poetry export --without-hashes --format=requirements.txt > requirements.txt
```

This project uses `black` for formatting. 
```shell
black .
```

Create and tag new releases (only the project owner can upload to PyPi):
```shell
zsh release.sh patch
zsh release.sh minor
zsh release.sh major
```