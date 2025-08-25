import re
import os
import shutil
import click

from urllib import request
from bs4 import BeautifulSoup
from config_loader import get_path


"""
A simple tool to automate the process of saving images from Flickr.  Currently takes any Flickr 
    image url and saved the highest resolution version of that image available to a local 
    directory of your choosing.

Potential future improvements:
- TODO: Make a standard "tool" class that all of the other tools draw from
    put in lib/
- TODO: Fold drive consolidator into this?
"""


class Fyllo:
    def __init__(self, pattern_match, replacement):
        # self.sct_home = get_path("sct_home")
        # self.source_dir = source_dir
        # self.target_dir = os.path.join(os.getenv("HOME"), target_dir)
        # self.retain_source = retain_source
        # self.ignore_patterns = [".DS_Store"]  # Placeholder solution
        # self.ignore_section_cnt = 2  # Placeholder solution
        # self.source_file_index = self.build_source_file_index()

        self.pattern_match = pattern_match
        self.replacement = replacement
        self.search_dir = os.getcwd()

    def run_phyllo_rename(self):
        """Runs the following consolidation logic steps:
        1. Identifies the common directory hierarchy under the source's top-level subdirectories
        2. Creates the user-suplied target directory if it does not exist
        3. Recreates the source's common directory hierarchy under the user-suplied target directory
        4. Either copies or moves files from the source to the target
        """
        self.rename_files_in_directory()

    def rename_files_in_directory(self):
        """
        Rename files in the given self.search_dir if their names match the regex self.pattern_match.

        Args:
            self.search_dir (str): The path to the self.search_dir containing files to rename.
            self.pattern_match (str): The regex self.pattern_match to match filenames.
            self.replacement (str): The self.replacement string for the new filenames.
        """
        for filename in os.listdir(self.search_dir):
            match = re.match(self.pattern_match, filename)
            if match:
                new_name = re.sub(self.pattern_match, self.replacement, filename)
                old_path = os.path.join(self.search_dir, filename)
                new_path = os.path.join(self.search_dir, new_name)
                print(f"Renaming: {filename} → {new_name}")
                os.rename(old_path, new_path)


@click.command()
@click.option(
    "--pattern_match",
    # default=".",  # Current default assumes that you are runnning the script from the source directory
    prompt="What files should we look for?",
)
@click.option(
    "--replacement",
    # default="",  # Current default is related to local testing
    prompt="What should we call them?",
)
def run_phyllo(pattern_match: str, replacement: str):
    fyllo = Fyllo(pattern_match=pattern_match, replacement=replacement)
    fyllo.run_phyllo_rename()


if __name__ == "__main__":
    run_phyllo()
