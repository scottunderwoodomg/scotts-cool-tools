import re
from urllib import request
from bs4 import BeautifulSoup
from lib.config_loader import load_config
import click

"""
A simple tool to automate the process of saving images from Flickr.  Currently takes any Flickr 
    image url and saved the highest resolution version of that image available to a local 
    directory of your choosing.

Potential future improvements:
- TODO: Ability to specify file format for image that is saved
- TODO: Implement an easier way to run the command, potentially pulling the url from clipboard?
- TODO: Introduce the ability to select an image version other than the highest resolution available
"""


def sizes_page_redirect(url: str) -> str:
    """Parses the url for a Flickr image page and returns the url
    for the "sizes" page corresponding with that image
    """
    return "/".join(url.split("/")[0:6]) + "/sizes"


def parse_image_link(url) -> str:
    """Parses the Flickr image link html object to return just
    the url itself.
    """
    return str(url).split('"')[1]


def return_largest_size_number_key(d: dict) -> str:
    """Returns the dictionary key corresponding with the highest
    corresponding value from a dictionary comprised entirely of
    str: int key value pairs.
    """
    return max(d, key=d.get)


def isolate_image_title(soup) -> str:
    """Parses the Flickr image title html object to return the raw
    title by itself.
    """
    title_obj_string = str(soup.find_all("title"))
    return title_obj_string.split(" | ")[1]


def clean_image_title(title_string: str) -> str:
    """Normalizes the title string of a given Flickr image by:
    - Removing special characters
    - Changing all letters to lowercase
    - Replacing spaces with underscores
    """
    return "_".join(re.sub(r"[^a-zA-Z0-9\s]", "", title_string).split(" ")).lower()


def isolate_image_link(soup) -> str:
    """Parses the html related to image version sizes to isolate
    the distinct urls related to each size version.
    """
    size_images = soup.find(id="allsizes-photo")

    image_list = size_images.find_all("img")

    return parse_image_link(image_list[0])


def parse_image_size(image_url: str) -> int:
    """Parses the html related to image version sizes to isolate
    each numeric size and return it as an int.
    """
    image_size_section = image_url.split(">")[1].split(" ")
    if len(image_size_section) < 2:
        return 0
    elif "K" in image_size_section[1]:
        return 1000000
    else:
        return int(image_size_section[1].split("<")[0])


def identify_largest_version(html) -> str:
    """Scans inptut html for a given Flickr image page to
    isolate the section that lists the various sizes of
    the image that at hosted on the site.

    It then parses that information so that each size and
    the corresponding url are plased into a dictionary called
    image_size_links.

    The function finally returns the url assoicated with the
    largest image size from the image_size_links dict.
    """
    soup = BeautifulSoup(html, "html.parser")

    size_images = soup.find(id="all-sizes-header")
    image_size_options = size_images.find_all("a")

    image_size_links = {
        parse_image_link(str(i)): parse_image_size(str(i))
        for i in image_size_options
        if "sizes" in str(i)
    }

    largest_image_key = return_largest_size_number_key(image_size_links)

    return str(largest_image_key).split("sizes/")[1]


def return_image_data(link: str) -> tuple:
    """Parses the html of a given Flickr image page and returns:
    - The image title (formatted to remove spaces and spec chars)
    - The direct link to the image itself
    """
    largest_resource = request.urlopen(link)
    soup = BeautifulSoup(largest_resource, "html.parser")
    image_title = clean_image_title(isolate_image_title(soup))
    largest_image_link = isolate_image_link(soup)

    return largest_image_link, image_title


def identify_largest_image_version_url(url: str) -> str:
    """For a given Flickr image, scans the information for all
    different versions of that image hosted on Flickr.  It
    then identifies the version with the highest resolution
    and returns the associated url.
    """
    resource = request.urlopen(url + "/sq/")

    largest_img_char = identify_largest_version(resource)

    return url + "/" + largest_img_char


def save_image(link, save_path, filename):
    """Saves image found at provided link to the path indicated
    and under the provided filename
    """
    request.urlretrieve(link, f"{save_path}/{filename}.jpg")


@click.command()
@click.option(
    "--url",
    prompt="What URL are you saving?",
)
@click.option(
    "--save_path",
    default=load_config()["local_paths"]["file_save_dir"],
    prompt="Where do you want this saved?",
)
def image_download(url: str, save_path: str):
    """Saves the image from a given Flickr page to the location
    of your choice
    """
    sizes_page = sizes_page_redirect(url)

    largest_image_link = identify_largest_image_version_url(sizes_page)

    image_dl_link, image_title = return_image_data(largest_image_link)

    save_image(image_dl_link, save_path, image_title)


if __name__ == "__main__":
    image_download()
