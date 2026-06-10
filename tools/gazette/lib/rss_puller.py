import feedparser
import calendar
import re
from datetime import datetime, timezone
import os

from config_loader import get_path



# ─────────────────────────────────────────────

class RssPuller():
    def __init__(self):
        self.sct_home = get_path("sct_home")
        self.script_dir  = get_path("file_save_dir")
        # self.source_dir = source_dir
        # self.target_dir = os.path.join(os.getenv("HOME"), target_dir)
        # self.retain_source = retain_source
        # self.ignore_patterns = [".DS_Store"]  # Placeholder solution

        #self.pattern_match = pattern_match
        # ─────────────────────────────────────────────
        # CONFIGURATION — edit these three variables
        # ─────────────────────────────────────────────

        # Add as many feed URLs as you like.
        # Single feed example  : rss_feeds = ["https://feeds.bbci.co.uk/news/rss.xml"]
        # Multiple feeds example:
        self.rss_feeds = [
            "https://gothamist.com/feed",
            #"https://www.nydailynews.com/arc/outboundfeeds/rss/section/new-york/range/display_date/now-5d/now/?outputType=xml&size=50",
            #"https://www.nydailynews.com/arc/outboundfeeds/rss/section/news_politics_new-york-elections-government/range/display_date/now-5d/now/?outputType=xml&size=50"
            "http://www.ny1.com/services/contentfeed.nyc%7Call-boroughs%7Cnews.landing.rss",
            "http://www.ny1.com/services/contentfeed.nyc%7Call-boroughs%7Cnews%7Ctransit.landing.rss",
            "http://www.ny1.com/services/contentfeed.nyc%7Call-boroughs%7Cnews%7Ceducation.landing.rss",
            "http://www.ny1.com/services/contentfeed.nyc%7Cbrooklyn.hero.rss",
            "http://www.ny1.com/services/contentfeed.nyc%7Call-boroughs%7Cweather%7Cweather-blogs.hero.rss"
            "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
            "https://nypost.com/feed/"
        ]

        self.start_date = "2026-06-07"  # YYYY-MM-DD
        self.end_date   = "2026-06-08"  # YYYY-MM-DD

    def run_rss_puller(self):
        """Runs the following:"""
        self.main()


    def parse_date(self, date_str):
        """Parse a YYYY-MM-DD string into an aware UTC datetime."""
        return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)


    def entry_published_dt(self, entry):
        """Return a timezone-aware datetime for a feed entry, or None if unavailable."""
        time_struct = entry.get("published_parsed") or entry.get("updated_parsed")
        if not time_struct:
            return None
        timestamp = calendar.timegm(time_struct)
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)


    def pull_articles(self, feed_url, start_dt, end_dt):
        """Fetch a single feed and return matched (datetime, entry, feed_url) tuples."""
        print(f"  Fetching: {feed_url}")
        feed = feedparser.parse(feed_url)

        if feed.bozo and not feed.entries:
            raise ValueError(f"Could not parse feed — {feed.bozo_exception}")

        matched = []
        for entry in feed.entries:
            pub_dt = self.entry_published_dt(entry)
            if pub_dt is None:
                continue
            if start_dt <= pub_dt <= end_dt:
                matched.append((pub_dt, entry, feed_url))

        print(f"    → {len(matched)} article(s) matched")
        return matched


    def format_summary(self, entry):
        """Strip HTML from an entry summary and word-wrap at ~80 chars."""
        summary = entry.get("summary", "")
        if not summary:
            return ""
        summary = re.sub(r"<[^>]+>", "", summary).strip()
        words, line, lines = summary.split(), "", []
        for word in words:
            if len(line) + len(word) + 1 > 80:
                lines.append(line)
                line = word
            else:
                line = f"{line} {word}".strip()
        if line:
            lines.append(line)
        return lines


    def write_output(self, all_articles, feeds, start, end):
        """Write all collected articles to rss_output.txt, grouped by feed."""
        output_path = os.path.join(self.script_dir, "rss_output.txt")

        # Group by feed URL, preserving order
        by_feed = {url: [] for url in feeds}
        for pub_dt, entry, feed_url in all_articles:
            by_feed[feed_url].append((pub_dt, entry))

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("RSS ARTICLE PULL\n")
            f.write("=" * 60 + "\n")
            f.write(f"Feeds     : {len(feeds)}\n")
            f.write(f"Date range: {start} to {end}\n")
            f.write(f"Articles  : {len(all_articles)} total\n")
            f.write(f"Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n")

            global_index = 1

            for feed_url in feeds:
                articles = by_feed[feed_url]
                f.write(f"\n{'─' * 60}\n")
                f.write(f"FEED: {feed_url}\n")
                f.write(f"Articles in range: {len(articles)}\n")
                f.write(f"{'─' * 60}\n\n")

                if not articles:
                    f.write("No articles found in the specified date range.\n\n")
                    continue

                for pub_dt, entry in articles:
                    f.write(f"[{global_index}] {entry.get('title', 'No title')}\n")
                    f.write(f"    Published : {pub_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
                    f.write(f"    Link      : {entry.get('link', 'N/A')}\n")
                    summary_lines = self.format_summary(entry)
                    for ln in summary_lines:
                        f.write(f"    {ln}\n")
                    f.write("\n")
                    global_index += 1

        return output_path


    def main(self):
        if not self.rss_feeds:
            print("ERROR: rss_feeds is empty. Add at least one feed URL.")
            return

        start_dt = self.parse_date(self.start_date)
        end_dt   = self.parse_date(self.end_date).replace(hour=23, minute=59, second=59)

        print(f"Pulling {len(self.rss_feeds)} feed(s) from {self.start_date} to {self.end_date}…\n")

        all_articles = []
        errors       = []

        for url in self.rss_feeds:
            try:
                matched = self.pull_articles(url, start_dt, end_dt)
                all_articles.extend(matched)
            except ValueError as e:
                print(f"  WARNING: Skipping feed — {e}")
                errors.append((url, str(e)))

        # Sort everything chronologically across all feeds
        all_articles.sort(key=lambda x: x[0])

        output_path = self.write_output(all_articles, self.rss_feeds, self.start_date, self.end_date)

        print(f"\nDone. {len(all_articles)} total article(s) written to: {output_path}")
        if errors:
            print(f"\n{len(errors)} feed(s) had errors:")
            for url, err in errors:
                print(f"  • {url}\n    {err}")

