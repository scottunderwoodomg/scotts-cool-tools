import os

import shutil
from pathlib import Path
from datetime import datetime
from config_loader import get_path
import click

"""
Improvements Needed

- TODO: Clean up the MVP code and make a bit more personal
- TODO: Add click interface for selecting a template but the option to overide and just create a quick note

- TODO: Capture other system information for a system report note (python version, etc., team name [derived from directory?])
- TODO: Consolidate redundant lines of code
- TODO: Add tags and make an easy "list notes" function for the tool?
- TODO: Notes Search (ordered by stuff)
- TODO: Ability to move all of the notes to a single location or interact with them en masse
- TODO: Add the ablity to open it in your editor of choice
- TODO: Add docstrings and type hints
- TODO: Create additional template types from my list in notion: 
        - Make a bunch of project management/notes/incident report txt file templates
        - Meeting notes
        - PRD 
"""


class NoteCreator:
    def __init__(self, requested_template, file_name):
        self.file_name = file_name
        self.sct_home = get_path("sct_home")
        self.text_editor_path = get_path("text_editor")
        self.working_directory = Path.cwd()
        self.requested_template = requested_template
        # make method to build file name
        self.destination_path_string = f"{self.working_directory}/{self.file_name}.md"

    def run_creator(self):
        self.copy_template()
        self.populate_template(self.set_dynamic_values())
        self.open_editor()

    def set_dynamic_values(self):
        # Step 3: Define dynamic values to replace in the markdown file
        dynamic_values = {
            # "{{username}}": "John Doe",
            "{{ date }}": datetime.now().strftime("%Y-%m-%d"),
            "{{ time }}": datetime.now().strftime("%Y-%m-%d"),
            "{{ topic }}": self.file_name,
        }

        return dynamic_values

    def copy_template(self):
        # Step 1: Define the source and destination paths
        source_path = Path(
            f"{self.sct_home}/tools/notato/templates/{self.requested_template}.md"
        )

        # Step 2: Copy the markdown file from source to destination
        shutil.copy(source_path, Path(self.destination_path_string))

    def populate_template(self, dynamic_values):
        # Step 4: Read the copied markdown file, replace placeholders, and write changes
        with open(Path(self.destination_path_string), "r") as file:
            content = file.read()

        # Step 5: Replace the placeholders with dynamic values
        for placeholder, replacement in dynamic_values.items():
            content = content.replace(placeholder, replacement)

        # Step 6: Write the modified content back to the file
        with open(Path(self.destination_path_string), "w") as file:
            file.write(content)

    def open_editor(self):
        # Open the file you just created in the text editor of your choice
        os.system(
            f"open -a '{self.text_editor_path}' '{self.working_directory}/{self.file_name}.md'"
        )


@click.command()
@click.option(
    "--requested_template",
    default="quick_note",
    prompt="What kind of note are you creating?",
)
@click.option(
    "--file_name",
    default="new_file",
    prompt="What should the note be called?",
)
def run_notato(requested_template: str, file_name: str):
    """Saves the image from a given Flickr page to the location
    of your choice
    """
    creator = NoteCreator(requested_template=requested_template, file_name=file_name)
    creator.run_creator()


if __name__ == "__main__":
    run_notato()
