import re
import os
import shutil
import click

from config_loader import get_path

from lib.rss_puller import RssPuller
from lib.feed_summarizer import FeedSummarizer

"""
Info goes here

Potential future improvements:

"""


class Gazette:
    def __init__(self):
        self.sct_home = get_path("sct_home")
        self.puller = RssPuller()
        self.summarizer = FeedSummarizer()

    def publish_gazette(self):
        """Runs the following:"""
        self.puller.run_rss_puller()
        if self.check_for_news():
            self.summarizer.run_feed_summarizer()
        else:
            print("nothing new in the news")

    def check_for_news(self,file_a, file_b):
        with open(file_a, "r", encoding="utf-8") as f:
            content_a = f.read()

        if os.path.exists(file_b):
            with open(file_b, "r", encoding="utf-8") as f:
                content_b = f.read()
        else:
            content_b = None

        if content_a == content_b:
            print(f"Files are identical. No changes made.")
        else:
            shutil.copy2(file_a, file_b)
            os.remove(file_a)
            print(f"Files differed. '{file_b}' updated and '{file_a}' deleted.")


@click.command()
def run_gazette():
    gazette = Gazette()
    gazette.publish_gazette()


if __name__ == "__main__":
    run_gazette()
