from urllib import request
from bs4 import BeautifulSoup
import click

"""
TODO: Ability to specify file format
TODO: Quicker way to run the command, Pull url from clipboard?
TODO: Variable image size selection
"""


def sizes_page_redirect(url):
    print("/".join(url.split("/")[0:6]) + "/sizes")
    return "/".join(url.split("/")[0:6]) + "/sizes"


def identify_largest_version(html):
    soup = BeautifulSoup(html, "html.parser")

    # print(soup.find("ol", "sizes-list").find_next(text=True).strip())
    # print(soup.find("ol", "sizes-list").strip())
    size_images = soup.find(id="all-sizes-header")
    # print(size_images)
    largest_image = size_images.find_all("li")[-2]  # [-1]  # .get_text() # .strip()
    # print(type(largest_image))
    # print(largest_image)

    image_char = str(largest_image).split("sizes/")
    # print(image_char)
    return image_char[1][0]


def isolate_image_link(html):
    soup = BeautifulSoup(html, "html.parser")

    # print(soup.find("ol", "sizes-list").find_next(text=True).strip())
    # print(soup.find("ol", "sizes-list").strip())
    size_images = soup.find(id="allsizes-photo")
    # print(size_images)
    largest_image = str(
        size_images.find_all("img")[0]
    )  # [-1]  # .get_text() # .strip()
    # print(type(largest_image))
    print(largest_image)
    largest_image_2 = largest_image.split('"')[1]
    largest_image_3 = largest_image.split("//")[1]
    print(largest_image_3)

    ##image_char = str(largest_image).split("sizes/")

    ##return image_char[1][0]

    return largest_image_3


def isolate_image_object(html):
    image_class = html.split(
        "view photo-well-media-scrappy-view requiredToShowOnServer"
    )[1]
    return image_class.split('src="//')[1]


def extract_image_link(obj):
    return obj.split('"')[0]


def extract_filename(obj):
    file_name = obj.split('alt="')[1]
    return file_name.split('"')[0].replace(" ", "_")


def save_image(link, save_path, filename):
    request.urlretrieve(f"http://{link}", f"{save_path}/{filename}.jpg")


@click.command()
@click.option(
    "--url",
    default="https://www.flickr.com/photos/68689268@N07/7846550050/in/gallery-134638499@N05-72157721540942226/",
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
    resource = request.urlopen(sizes_page)
    # print(resource)
    largest_img_char = identify_largest_version(resource)

    largest_image_link = sizes_page + "/" + largest_img_char
    print(largest_image_link)

    largest_resource = request.urlopen(largest_image_link)

    image_dl_link = isolate_image_link(largest_resource)

    save_image(image_dl_link, save_path, filename="this_is_the_image")

    # <div id="allsizes-photo">
    # 	<img src="https://live.staticflickr.com/7280/7846550050_550d2d50e8_k.jpg">
    # </div>

    """
    html = resource.read().decode(resource.headers.get_content_charset())
    image_object = isolate_image_object(html)  
    image_link = extract_image_link(image_object)
    file_name = extract_filename(image_object)

    """


if __name__ == "__main__":
    image_download()
