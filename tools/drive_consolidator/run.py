import os

import shutil
from config_loader import get_path
import click

"""
When downloading a backup copy of Google Drive, the contents will retain their directory structure and hierarchy 
but will be broken up across multiple downloads due to Google-imposed download file size limitations.  This 
results in a set of # top-level folders that contain various randomized parts of the original content which is 
harder to interact with.

The DriveConsolidator defined in this file will:
    1. Recursively scan a source directory and create an index of the files it contains as well as 
        their respective paths
    2. Replicate the "common directory sttructure" shared across the source's top-level directories 
        at a specified target location.
    3. Either copy or move the files from the source to the unified target locations

TODOs:
    - TODO: Try to find a more elegant way to define file that should be ignored.  Currently uses
        - self.ignore_patterns list
        - is_ignored() method
    - TODO: Find a more intuitive/dynamic way than self.ignore_section_cnt = 2 to ignore directories at
        the start of the path that should not be recreated
    - TODO: Replace this click default for target_dir with something more general or remove the 
        default entirely
    - TODO: Potentially add more protections against files accidentally being removed from the source:
        - Only copy files in the main script but add a "cleanup source" argment that can be explicitly 
            called if needed and run on its own?
"""


class DriveConsolidator:
    def __init__(self, source_dir, target_dir, retain_source):
        self.sct_home = get_path("sct_home")
        self.source_dir = source_dir
        self.target_dir = os.path.join(os.getenv("HOME"), target_dir)
        self.retain_source = retain_source
        self.ignore_patterns = [".DS_Store"]  # Placeholder solution
        self.ignore_section_cnt = 2  # Placeholder solution
        self.source_file_index = self.build_source_file_index()

    def run_consolidator(self):
        """Runs the following consolidation logic steps:
        1. Identifies the common directory hierarchy under the source's top-level subdirectories
        2. Creates the user-suplied target directory if it does not exist
        3. Recreates the source's common directory hierarchy under the user-suplied target directory
        4. Either copies or moves files from the source to the target
        """
        self.common_dir_hierarchy = self.produce_common_dir_hierarchy()
        self.create_path_if_not_exist(self.target_dir)
        self.replicate_common_dirs(self.common_dir_hierarchy)
        print("Beginning file transfer")
        self.run_file_transfer()
        print("File transfer complete")

    def is_ignored(self, root, file) -> bool:
        """Placeholder method that is used to ignore certain files under the source directory
        to that they are excluded from the source_file_index.  Currently, the criteria for
        exclusion include:
            - A file whose name is captured in list self.ignore_patterns
            - A file that is located at the top level directory of the source
        """
        if file in self.ignore_patterns or root.count("/") < 1:
            return True
        else:
            return False

    def build_source_file_index(self) -> list:
        """Recursively scans the source directory and creates an index of the files it contains
        along with their respective paths
        """
        file_list = []
        for root, dirs, files in os.walk(self.source_dir):
            for file in files:
                if not self.is_ignored(root, file):
                    file_list.append(os.path.join(root, file))
        return file_list

    def produce_common_dir_hierarchy(self) -> list:
        """Takes the files and paths captured in self.source_file_index and returns a
        distinct list of the directories referenced
        """
        common_dir_hierarchy = []
        for file in self.source_file_index:
            split_path = file.split("/")
            just_path = "/".join(
                split_path[self.ignore_section_cnt : len(split_path) - 1]
            )

            if len(just_path) > 0:
                common_dir_hierarchy.append(just_path)

        return set(common_dir_hierarchy)

    def create_path_if_not_exist(self, path):
        """Checks if a directory taht we plan to write data to exists already and
        creates it if that is not the case
        """
        if not os.path.exists(path):
            print(f"Creating target path: {path}")
            os.makedirs(path)

    def replicate_common_dirs(self, dir_list):
        """Recreates the distinct paths captured in self.common_dir_hierarchy
        under the user-suplied target directory
        """
        for directory in dir_list:
            path = os.path.join(self.target_dir, directory)
            self.create_path_if_not_exist(path)

    def create_src_tgt_sets(self) -> list:
        """Creates a list of dictionaries where:
        - Each disctionary in the list corresponds with a file that needs
            to be moved from the source to the target
        - Each dictionary has a "src" and "tgt" key which contain the path
            to the source file and the path to the file under its new target
            locaton respectively
        """
        return [
            {
                "src": file,
                "tgt": os.path.join(
                    self.target_dir,
                    "/".join(file.split("/")[self.ignore_section_cnt :]),
                ),
            }
            for file in self.source_file_index
        ]

    def run_file_transfer(self):
        """Creates the list of file movement instructions by running method
        create_src_tgt_sets() and loops through each file in the list to
        either:
        - IF self.retain_source -> copy the file from src to tgt
        - IF NOT self.retain_source -> move the file from src to tgt
        """
        for file in self.create_src_tgt_sets():
            print(f"Copying file: {file["src"]}")
            if self.retain_source:
                shutil.copyfile(file["src"], file["tgt"])
            else:
                shutil.move(file["src"], file["tgt"])


@click.command()
@click.option(
    "--source_dir",
    default=".",  # Current default assumes that you are runnning the script from the source directory
    prompt="What top-level directory are the source files located in?",
)
@click.option(
    "--target_dir",
    default="desktop/path_recreation",  # Current default is related to local testing
    prompt="What top-level directory should the consolidated copy be created under?",
)
@click.option(
    "--retain_source",
    default=True,
    prompt="Would you like retain the source as is?",
)
def run_drive_consolidator(source_dir: str, target_dir: str, retain_source: bool):
    consolidator = DriveConsolidator(
        source_dir=source_dir, target_dir=target_dir, retain_source=retain_source
    )
    consolidator.run_consolidator()


if __name__ == "__main__":
    run_drive_consolidator()
