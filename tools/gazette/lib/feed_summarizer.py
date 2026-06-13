import os
import anthropic
from datetime import datetime

from config_loader import load_config
from config_loader import get_path
from config.gazette_config import gazette_config


class FeedSummarizer():
    def __init__(self):
        # ─────────────────────────────────────────────
        # CONFIGURATION — edit these variables
        # ─────────────────────────────────────────────
        self.ANTHROPIC_API_KEY = load_config()["ANTHROPIC_API_KEY"]
        self.MODEL = gazette_config["model"]

        # Interests filter.
        # List any topics you care about. Only articles that are relevant to at least
        # one of these interests will be included in the digest.
        # Set to an empty list [] to include ALL articles regardless of topic.
        self.INTERESTS = gazette_config["interests"]

        # File paths (default: same directory as this script)
        self.SCRIPT_DIR   = get_path("file_save_dir")
        self.INPUT_FILE   = os.path.join(self.SCRIPT_DIR, "latest_rss_output.txt")
        self.OUTPUT_FILE  = os.path.join(self.SCRIPT_DIR, "rss_summary.txt")

    # ─────────────────────────────────────────────

    def run_feed_summarizer(self):
        """Runs the following:"""
        self.main()

    def read_articles(self, path):
        """Read the rss_output.txt file and return its raw contents."""
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Input file not found: {path}\n"
                "Run rss_puller.py first to generate rss_output.txt."
            )
        with open(path, "r", encoding="utf-8") as f:
            return f.read()


    def build_filter_prompt(self, raw_text, interests):
        """
        Ask Claude to return only the articles relevant to the given interests,
        preserving the original text block for each matched article verbatim.
        """
        interests_list = "\n".join(f"- {i}" for i in interests)
        return f"""You are a content filter. Below is a list of news articles, each separated by a blank line and starting with a numbered heading like [1], [2], etc.

    I am only interested in articles related to ANY of these topics:
    {interests_list}

    Instructions:
    - Read every article carefully.
    - Return ONLY the full text blocks of articles that are clearly relevant to at least one of the listed topics.
    - Interpret topics broadly and use good judgement — e.g. "schools" should match articles about education, teachers, students, universities, curriculum, etc.
    - Preserve each matching article's text exactly as it appears in the input.
    - Separate each returned article block with a blank line.
    - If NO articles match, respond with exactly: NO_MATCHES

    Do NOT add commentary, headings, or any extra text — only the matching article blocks (or NO_MATCHES).

    --- ARTICLES START ---
    {raw_text}
    --- ARTICLES END ---
    """


    def build_summary_prompt(self, filtered_text, interests):
        """Construct the summarisation prompt for the filtered article set."""
        interests_str = ", ".join(f'"{i}"' for i in interests)
        interest_note = (
            f"These articles were pre-filtered to topics matching: {interests_str}.\n"
            if interests
            else ""
        )
        return f"""Below is a collection of RSS news articles with their titles, publication dates, links, and summaries.
    {interest_note}
    Your task:
    1. Identify the major themes or topics across all the articles.
    2. For each theme, write a concise 1–2 sentence description.
    3. Under each theme, list the most relevant articles as bullet points using this exact format:
    - [Article Title](URL) — one-sentence relevance note

    Rules:
    - Keep the overall output tight and scannable.
    - Every article bullet must include the hyperlink in Markdown format.
    - If an article fits multiple themes, you may list it under more than one.
    - Do not invent information; only use what is in the articles provided.
    - Use plain Markdown (headers with ##, bullet points with -).

    --- ARTICLES START ---
    {filtered_text}
    --- ARTICLES END ---
    """


    def filter_articles(self, raw_text, interests, client, model):
        """
        Use Claude to filter the article list down to those matching INTERESTS.
        Returns the filtered text, or None if nothing matched.
        """
        print(f"  Filtering articles for interests: {interests}")
        message = client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": self.build_filter_prompt(raw_text, interests)}],
        )
        result = message.content[0].text.strip()
        if result == "NO_MATCHES":
            return None
        return result


    def summarise_articles(self, filtered_text, interests, client, model):
        """Send filtered articles to Claude and return the themed summary."""
        message = client.messages.create(
            model=model,
            max_tokens=2048,
            messages=[{"role": "user", "content": self.build_summary_prompt(filtered_text, interests)}],
        )
        return message.content[0].text


    def write_summary(self, summary, interests, output_path):
        """Write the summary to a text file."""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("RSS ARTICLE SUMMARY\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Source    : {self.INPUT_FILE}\n")
            f.write(f"Model     : {self.MODEL}\n")
            if interests:
                f.write(f"Interests : {', '.join(interests)}\n")
            else:
                f.write("Interests : all articles (no filter applied)\n")
            f.write("=" * 60 + "\n\n")
            f.write(summary)
            f.write("\n")


    def main(self):
        # ── Validate API key ──────────────────────────────────────────
        if not self.ANTHROPIC_API_KEY:
            print(
                "ERROR: No Anthropic API key found.\n"
                "Set the ANTHROPIC_API_KEY environment variable, or paste your key\n"
                "directly into the ANTHROPIC_API_KEY variable at the top of this script.\n"
                "Get a key at: https://console.anthropic.com/settings/keys"
            )
            return

        client = anthropic.Anthropic(api_key=self.ANTHROPIC_API_KEY)

        # ── Read articles ─────────────────────────────────────────────
        print(f"Reading articles from: {self.INPUT_FILE}")
        try:
            raw_text = self.read_articles(self.INPUT_FILE)
        except FileNotFoundError as e:
            print(f"ERROR: {e}")
            return

        # ── Filter (if interests are defined) ─────────────────────────
        try:
            if self.INTERESTS:
                print(f"Step 1/2 — Filtering by interests ({len(self.INTERESTS)} topic(s))…")
                filtered_text = self.filter_articles(raw_text, self.INTERESTS, client, self.MODEL)
                if filtered_text is None:
                    print(
                        "No articles matched your INTERESTS filter. "
                        "Try broadening your topics or set INTERESTS = [] to include everything."
                    )
                    return
            else:
                print("No interests filter set — summarising all articles.")
                filtered_text = raw_text

            # ── Summarise ─────────────────────────────────────────────
            step = "2/2" if self.INTERESTS else "1/1"
            print(f"Step {step} — Summarising with Claude ({self.MODEL})…")
            summary = self.summarise_articles(filtered_text, self.INTERESTS, client, self.MODEL)

        except anthropic.AuthenticationError:
            print(
                "ERROR: API key rejected. Check your key at:\n"
                "https://console.anthropic.com/settings/keys"
            )
            return
        except anthropic.APIError as e:
            print(f"ERROR: Anthropic API error — {e}")
            return

        # ── Write output ──────────────────────────────────────────────
        self.write_summary(summary, self.INTERESTS, self.OUTPUT_FILE)
        print(f"Done. Summary written to: {self.OUTPUT_FILE}")
