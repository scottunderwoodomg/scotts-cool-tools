from setuptools import setup, find_packages

"""
TODO: Need to be able to add this to zshrc
###################################
# Scotts Cool Tools
alias sct="~/Documents/GitHub/scotts-cool-tools/toolbox.sh"
export SCT_HOME='/Users/scott/Documents/GitHub/scotts-cool-tools'
###################################
"""

setup(
    name="my_lib",
    version="0.1",
    packages=find_packages(where="lib"),
    package_dir={"": "lib"},
)
