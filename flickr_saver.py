import re
from urllib import request
from bs4 import BeautifulSoup
import click

"""
TODO: Ability to specify file format
TODO: Quicker way to run the command, Pull url from clipboard?
TODO: Variable image size selection
"""
# TODO: Rebuild as a class
# TODO: move all nested cleaning steps to their own functions


def sizes_page_redirect(url):
    return "/".join(url.split("/")[0:6]) + "/sizes"


def parse_image_link(url):
    return str(url).split('"')[1]


def return_largest_size_number_key(d):
    return max(d, key=d.get)


def isolate_image_title(soup):
    title_obj_string = str(soup.find_all("title"))
    return title_obj_string.split(" | ")[1]


def clean_image_title(title_string):
    return "_".join(re.sub(r"[^a-zA-Z0-9\s]", "", title_string).split(" "))


def isolate_image_link(soup):
    size_images = soup.find(id="allsizes-photo")

    image_list = size_images.find_all("img")

    return parse_image_link(image_list[0])


def parse_image_size(image_url):
    image_size_section = image_url.split(">")[1].split(" ")
    if len(image_size_section) < 2:
        return 0
    elif "K" in image_size_section[1]:
        return 1000000
    else:
        return int(image_size_section[1].split("<")[0])


def identify_largest_version(html):
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


def return_image_data(link):
    largest_resource = request.urlopen(link)
    soup = BeautifulSoup(largest_resource, "html.parser")
    image_title = clean_image_title(isolate_image_title(soup))
    largest_image_link = isolate_image_link(soup)

    return largest_image_link, image_title


def identify_largest_image_version_url(url):
    resource = request.urlopen(url + "/sq/")

    largest_img_char = identify_largest_version(resource)

    return url + "/" + largest_img_char


def save_image(link, save_path, filename):
    request.urlretrieve(link, f"{save_path}/{filename}.jpg")


@click.command()
@click.option(
    "--url",
    # default="https://www.flickr.com/photos/68689268@N07/7846550050/in/gallery-134638499@N05-72157721540942226/",
    default="https://www.flickr.com/photos/161038124@N08/54016136594/in/pool-legominifigs/",
    prompt="What URL are you saving?",
)
@click.option(
    "--save_path",
    default="/Users/scott/Desktop/Images for Drive",
    prompt="Where do you want this saved?",
)
def image_download(url, save_path):
    """Saves the image from a given Flickr page to the location of your choice"""
    sizes_page = sizes_page_redirect(url)

    largest_image_link = identify_largest_image_version_url(sizes_page)

    image_dl_link, image_title = return_image_data(largest_image_link)

    save_image(image_dl_link, save_path, image_title)


if __name__ == "__main__":
    image_download()
