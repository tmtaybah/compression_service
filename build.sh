#!/bin/sh
# This script builds the dependencies of the project

which -s brew
if [[ $? != 0 ]] ; then
    xcode-select --install
    # Install Homebrew
    echo "Installing Homebrew..."
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
else
    brew install python3
fi
pip3 install -r requirements.txt
