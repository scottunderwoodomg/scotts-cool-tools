from urllib import request
from bs4 import BeautifulSoup
import click

"""
TODO: Ability to specify file format
TODO: Quicker way to run the command, Pull url from clipboard?
"""

def isolate_image_object(html):
    image_class = html.split("view photo-well-media-scrappy-view requiredToShowOnServer")[1]
    return image_class.split('src="//')[1]

def extract_image_link(obj):
     return obj.split('"')[0]

def extract_filename(obj):
    file_name = obj.split('alt="')[1]
    return file_name.split('"')[0].replace(" ","_")

def save_image(link,save_path,filename):
    request.urlretrieve(f"http://{link}", f"{save_path}/{filename}.jpg")

@click.command()
@click.option('--url', prompt='What URL are you saving?')
@click.option('--save_path', default="/Users/scott/Desktop/Images for Drive", prompt='Where do you want this saved?',)
def image_download(url, save_path):
    """Saves the image from a given Flickr page to the location of your choice"""
    resource = request.urlopen(url)
    html = resource.read().decode(resource.headers.get_content_charset())
    image_object = isolate_image_object(html)  
    image_link = extract_image_link(image_object)
    file_name = extract_filename(image_object)

    save_image(image_link,save_path,file_name)

if __name__ == '__main__':
    image_download()
