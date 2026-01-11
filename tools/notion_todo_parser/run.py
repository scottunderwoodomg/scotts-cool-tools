from bs4 import BeautifulSoup
import json
import re


def extract_label(li_tag):
    label_tag = li_tag.find(["span", "strong"])
    return label_tag.get_text(strip=True) if label_tag else li_tag.get_text(strip=True)


def extract_checkbox_status(li_tag):
    checkbox = li_tag.find("div", class_="checkbox")
    # print(checkbox)
    return "checkbox-on" in checkbox.get("class", []) if checkbox else False


def extract_element_id(li_tag):
    ul_parent = li_tag.find_parent("ul")
    if ul_parent:
        return ul_parent.get("id")


def extract_background_color(li_tag):
    ul_parent = li_tag.find_parent("ul", class_=lambda c: c and "block-color" in c)
    if ul_parent:
        for cls in ul_parent.get("class", []):
            if "block-color" in cls:
                print(cls)
                return cls
    return None


"""
This function works for ul parents but trying to use li instead to get the names

def derive_parent_chain(li_tag):
    #print(li_tag.find_parents("ul"))    
    chain_ids = [ul_parent.get("id") for ul_parent in li_tag.find_parents("ul")]
    print(chain_ids)
    return chain_ids
"""


def derive_parent_chain(li_tag):
    # print(li_tag.find_parents("ul"))
    # chain_ids = [ul_parent.get("id") for ul_parent in li_tag.find_parents("ul")]
    parent_chain = []

    for li_parent in li_tag.find_parents("li"):
        label_tag = li_parent.find(["span", "strong"])
        parent_chain.append(
            label_tag.get_text(strip=True) if label_tag else li_tag.get_text(strip=True)
        )

    print(parent_chain)
    return parent_chain


def parse_li(li_tag):
    label = extract_label(li_tag)
    checked = extract_checkbox_status(li_tag)
    background_color = extract_background_color(li_tag)
    element_id = extract_element_id(li_tag)
    parent_chain = derive_parent_chain(li_tag)

    item = {
        "type": "task",
        "label": label,
        "checked": checked,
        "children": [],
        "id": element_id,
        # TODO: What date does "unsorted" get placed under?
        # TODO: Want to add a date value to each object
        # TODO: Need to figure out how I want to represent nested todos with multiple levels?
        #   Probably everything is captured at the lowest possible level and there is then a lineage chain field?
        "parent_chain": parent_chain,
    }

    if background_color:
        item["background_color"] = background_color

    # Find any nested <ul class="to-do-list"> inside this <li> (even if wrapped in divs etc.)
    nested_uls = li_tag.find_all("ul", class_="to-do-list", recursive=True)
    for ul in nested_uls:
        # Make sure we're not re-processing unrelated nested lists (like grandchildren of other li's)
        # Only process lists that are direct or nested children of the current li
        if li_tag in ul.parents:
            # print(li_tag)
            for child_li in ul.find_all("li", recursive=False):
                item["children"].append(parse_li(child_li))

    return item


def parse_ul(ul_tag):
    print(ul_tag)
    items = []
    for li in ul_tag.find_all("li", recursive=False):
        # print(li)
        items.append(parse_li(li))
    return items


# Load and parse the HTML
with open("4_14_2025_Weekly_ToDo.html", "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "lxml")

# Find all "Completed Days" summary blocks
summary_tags = soup.find_all("summary", string="Completed Days")
all_completed_sections = []

for summary in summary_tags:
    details = summary.find_parent("details")
    if not details:
        continue

    # Look for all top-level <ul class="to-do-list"> blocks within this details section
    # Usually there will be only one, but we’ll be flexible
    top_uls = details.find_all("ul", class_="to-do-list", recursive=False)
    for ul in top_uls:
        parsed = parse_ul(ul)
        all_completed_sections.extend(parsed)

json_object = json.dumps(all_completed_sections, indent=2)

# Print as JSON
# print(json_object)

# Write JSON to file
with open("4_14_2025_Weekly_ToDo.json", "w") as outfile:
    outfile.write(json_object)
