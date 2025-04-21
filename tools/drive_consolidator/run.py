import os

import shutil
from pathlib import Path
from datetime import datetime
from config_loader import get_path
import click

"""
When downloading a backup copy of Google Drive, the contents will retain their directory structure / hierarchy 
but will be broken up across multiple downloads.  This results in a set of # top-level folders that contain 
various randomized parts of the original content that is harder to interact with.

Create a script that will:
    - Recursively scan a specified source directory and create an index of the files it contains as well as 
        their respective paths
    - Recursively copy files from the specified source directories into a uniform   

TODO: Add docstrings    
"""


class DriveConsolidator:
    def __init__(self, source_dir, target_dir, retain_source):

        self.sct_home = get_path("sct_home")
        self.source_dir = source_dir
        self.target_dir = os.path.join(os.getenv("HOME"), target_dir)
        self.retain_source = retain_source
        # TODO: Add ability to ignore certain file type, directory patterns, other
        self.ignore_patterns = [".DS_Store"]
        # TODO: Must be a better way to handle the "ignore section cnt"
        self.ignore_section_cnt = 2
        self.files_list = self.list_files_walk()

    def run_consolidator(self):
        self.common_dir_hierarchy = self.produce_common_dir_hierarchy()
        self.replicate_common_dirs(self.common_dir_hierarchy)
        self.run_file_transfer()

    def is_ignored(self, root, file):
        # TODO: Figure out a better way to ignore top-level files
        if file in self.ignore_patterns or root.count("/") < 1:
            return True
        else:
            return False

    def list_files_walk(self):
        file_list = []
        for root, dirs, files in os.walk(self.source_dir):
            for file in files:
                if not self.is_ignored(root, file):
                    file_list.append(os.path.join(root, file))
        print(file_list)
        return file_list

    def produce_common_dir_hierarchy(self):
        common_dir_hierarchy = []
        for file in self.files_list:
            split_path = file.split("/")
            just_path = "/".join(
                split_path[self.ignore_section_cnt : len(split_path) - 1]
            )

            if len(just_path) > 0:
                common_dir_hierarchy.append(just_path)

        return set(common_dir_hierarchy)

    def create_path_if_not_exist(self, path):
        if not os.path.exists(path):
            print(f"Creating target path: {path}")
            os.makedirs(path)

    def replicate_common_dirs(self, dir_list):
        self.create_path_if_not_exist(self.target_dir)

        for directory in dir_list:
            path = os.path.join(self.target_dir, directory)
            self.create_path_if_not_exist(path)

    def create_src_tgt_sets(self):
        return [
            {
                "src": file,
                "tgt": os.path.join(
                    self.target_dir,
                    "/".join(file.split("/")[self.ignore_section_cnt :]),
                ),
            }
            for file in self.files_list
        ]

    def run_file_transfer(self):
        for file in self.create_src_tgt_sets():
            if self.retain_source:
                shutil.copyfile(file["src"], file["tgt"])
            else:
                shutil.move(file["src"], file["tgt"])


@click.command()
@click.option(
    "--source_dir",
    default=".",
    # default=os.getcwd(),
    prompt="What top-level directory are the source files located in?",
)
@click.option(
    "--target_dir",
    # TODO: Replace this default value with a different preferred path?
    default="desktop/path_recreation",
    prompt="What top-level directory should the consolidated copy be created under?",
)
@click.option(
    "--retain_source",
    default=True,
    prompt="Would you like retain the source as is?",
)
def run_drive_consolidator(source_dir: str, target_dir: str, retain_source: bool):
    """Add docstring here"""
    consolidator = DriveConsolidator(
        source_dir=source_dir, target_dir=target_dir, retain_source=retain_source
    )
    consolidator.run_consolidator()


if __name__ == "__main__":
    run_drive_consolidator()
