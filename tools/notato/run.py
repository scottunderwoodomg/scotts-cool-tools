import os
import shutil
from pathlib import Path
from datetime import datetime
from config_loader import get_path

"""
Improvements Needed

- TODO: Clean up the MVP code and make a bit more personal
- TODO: Add click interface for selecting a template but the option to overide and just create a quick note

- TODO: Add the ability to inject date from run.py script (Jinja?)
- TODO: Capture other system information for a system report note (python version, etc.)
- TODO: Use Class
- TODO: Add tags and make an easy "list notes" function for the tool?
- TODO: Notes Search (ordered by stuff)
- TODO: Ability to move all of the notes to a single location or interact with them en masse
- TODO: Add the ablity to open it in your editor of choice
"""


sct_home = get_path("sct_home")
text_editor_path = get_path("text_editor")
requested_template = "quick_note"

working_directory = Path.cwd()

# Step 1: Define the source and destination paths
source_path = Path(f"{sct_home}/tools/notato/templates/{requested_template}.md")
destination_path = Path(f"{working_directory}/template_copy.md")

# Step 2: Copy the markdown file from source to destination
shutil.copy(source_path, destination_path)

# Step 3: Define dynamic values to replace in the markdown file
dynamic_values = {
    # "{{username}}": "John Doe",
    "{{ date }}": datetime.now().strftime("%Y-%m-%d"),
    "{{ time }}": datetime.now().strftime("%Y-%m-%d"),
}

# Step 4: Read the copied markdown file, replace placeholders, and write changes
with open(destination_path, "r") as file:
    content = file.read()

# Step 5: Replace the placeholders with dynamic values
for placeholder, replacement in dynamic_values.items():
    content = content.replace(placeholder, replacement)

# Step 6: Write the modified content back to the file
with open(destination_path, "w") as file:
    file.write(content)

# print(f"File copied and modified at: {destination_path}")
# Open the file you just created in the text editor of your choice
os.system(f"open -a '{text_editor_path}' '{working_directory}/template_copy.md'")
