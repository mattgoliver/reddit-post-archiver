"""Reddit Post Archiver.

Author: Matthew Oliver
Version: 1/17/2024
"""
import json  # Allows access to the .json login information file
import praw  # Allows access to Reddit's API
import sqlite3  # Allows for database management
import os  # Allows for checking if database exists
import uuid  # Allows for generation of unique file names
import urllib.request  # Allows for media downloading
from urllib.parse import urlparse  # Allows for url domain identification
import requests  # Allows for file type identification
import mimetypes  # Allows for file type identification
import time  # Allows for rate limiting
import sys  # Allows for usage of yt-dlp


DIR = os.getcwd()
DATA_DIR = DIR + "\\data\\"
DATABASE_NAME = "reddit-post-archive.sqlite3"
SEPARATOR = '-' * 80


# Initialization functions
def setup():
    """Creates the file structure and config file."""
    try:
        os.mkdir(DATA_DIR)
    except FileExistsError:
        print("Data folder found.")

    config = dict()

    config["REDDIT_CREDENTIALS"] = {"client_id": "", "client_secret": "", "username": "", "password": "", "user_agent": ""}
    config["DOWNLOAD"] = {"banned_websites": []}

    with open("config.json", "w") as config_file:
        json.dump(config, config_file, indent=2)

    sys.exit("[IMPORTANT] Please fill-in the config.json file before proceeding.")


def initialize_reddit_connection():
    """Connect to the Reddit API via PRAW.

    Returns:
        obj: Authenticated Reddit instance
    """
    reddit_credentials = secrets["REDDIT_CREDENTIALS"]
    reddit = praw.Reddit(
        client_id=reddit_credentials["client_id"],
        client_secret=reddit_credentials["client_secret"],
        password=reddit_credentials["password"],
        user_agent=reddit_credentials["user_agent"],
        username=reddit_credentials["username"]
    )

    print(f"PRAW: Successfully authenticated as user: {reddit.user.me()}")

    return reddit


def initialize_database_connection():
    """Connects to the post archive database, creates one if it doesn't exist.

    Returns:
        tup: Database connection and cursor
    """
    # If the database exists, then connect to it
    if os.path.isfile(DATABASE_NAME):
        connection = sqlite3.connect(DATABASE_NAME)
        cursor = connection.cursor()
        print(f"SQLLite3: Database exists. Successfully connected to '{DATABASE_NAME}'")

    # If the database does not exist, then create it and connect to it
    else:
        print(f"SQLLite3: Database does not exist. Creating '{DATABASE_NAME}'...")
        connection = sqlite3.connect(DATABASE_NAME)
        cursor = connection.cursor()
        cursor.execute("create table posts (id text, title text, author text, "
                             "content_text text, subreddit text, subreddit_size integer, "
                             "upvotes integer, ratio integer, file_name text, url text, "
                             "created integer, skip text)")
        print("SQLLite3: Database successfully created.")

    return connection, cursor


# Helper functions
def check_duplicate(post_id):
    """Check the archive to see if a URL has been downloaded before.

    Args:
        post_id (str): Post ID to check for duplicate

    Returns:
        bool: True/False for duplicate status
    """
    cursor.execute(f"select * from posts where id='{post_id}'")
    results = cursor.fetchall()

    # If there are any results, then it is a duplicate post
    if results:
        return True
    else:
        return False


# Processing functions
def archive_saved_posts(upvote=False, unsave=False, limit=100):
    """Retrieves all saved posts from user's profile.

    Args:
        upvote (bool): Upvote post once archived, default=False
        unsave (bool): Unsave post once archived, default=False
        limit (int): Amount of posts to save, default=100, max=100
    """
    posts = reddit.user.me().saved()

    for pos, post in enumerate(posts):
        # Stop processing posts once the set limit has been exceeded
        if pos+1 > limit:
            break

        pos_info = (pos+1, limit)

        # Ignore saved comments
        if str(type(post)) == "<class 'praw.models.reddit.comment.Comment'>":
            continue

        # Un-save and skip duplicate posts
        if check_duplicate(post.id):
            print(f"[{pos_info[0]}/{pos_info[1]}] Duplicate found: {post.title}")
            if unsave:  # Un-save post
                post.unsave()
            if upvote:
                try:  # Upvote post so that user sees that it has been saved
                    post.upvote()
                except:
                    print(f"[{pos_info[0]}/{pos_info[1]}] Archived Post - Cannot upvote.")
            continue

        # Download file and save the filename of the downloaded file
        filename = download(post, pos_info)

        # Continue to next post if there was no file to download
        if filename is None:
            print(f"[{pos_info[0]}/{pos_info[1]}] Empty post found: {post.title}")
            if unsave:
                post.unsave()
            continue

        # Add the downloaded file to the database
        archive(post, filename, pos_info)

        # Un-save post to prevent future download attempts
        if unsave:
            post.unsave()

        # Upvote posts after archival
        if upvote:
            try:
                post.upvote()
            except:
                print(f"[{pos_info[0]}/{pos_info[1]}] Archived Post - Cannot upvote.")

    # Separate main output from closing messages
    print(SEPARATOR)
    print("MAIN: Finished downloading and archiving posts.")


def download(post, pos_info=(1, 1), filename=""):
    """Downloads post at given url.

    Args:
          post (obj): Post to download.
          pos_info (tup): Queue information in the form of (current position, queue size)
          filename (str): Name to save download as, default=random

    Returns:
         str: File name
    """
    filename = ""
    url = post.url

    # Skip downloading if the url is part of a known banned website
    domain = urlparse(url).netloc.split('.')[-2]
    if domain in secrets["DOWNLOAD"]['banned_websites']:
        return None

    # Retrieve file type
    response = requests.get(url)
    content_type = response.headers['content-type']
    file_type = mimetypes.guess_extension(content_type)

    # Default to .mp4 if no file_type can be found
    if file_type is None:
        file_type = '.mp4'

    # Loop until unique file name is generated
    if filename == "":
        post_exists = True
        while post_exists is True:
            filename = DATA_DIR + str(uuid.uuid4().hex) + file_type

            if not os.path.isfile(filename):  # Check if file name already exists
                post_exists = False

    # Log archival progress in the terminal
    print(f"[{pos_info[0]}/{pos_info[1]}] Downloading post: '{post.title}', file type: '{file_type}'.")

    # Download videos with yt-dlp
    if file_type == ".mp4":  # Download video files with yt-dlp
        print(f"[{pos_info[0]}/{pos_info[1]}] YT-DLP: '{filename}' downloading.")
        os.system(f'yt-dlp -o {filename} {url}')

    # Download images/GIFs with urllib
    else:
        try:
            urllib.request.urlretrieve(url, filename)
            print(f"[{pos_info[0]}/{pos_info[1]}] SUCCESS: '{filename}' downloaded.")
            time.sleep(1)  # Slow down download requests
        except urllib.error.HTTPError:  # Catch HTTP 404 errors.
            print(f"[{pos_info[0]}/{pos_info[1]}] ERROR: '{filename}' returns Error 404.")
            return None

    return filename


def archive(post, filename, pos_info=(1, 1)):
    """Archives the post at the given url.

    Information archived: ID, title, author, content (text & media), subreddit, url, date, amount
    and ratio of upvotes.

    Args:
        post: Post to archive.
        filename: Name of downloaded file to associate post information with.
        pos_info (tup): Queue information in the form of (current position, queue size)
    """
    # Find the subscriber count of the post's subreddit
    subreddit_size = int(reddit.subreddit(str(post.subreddit)).subscribers)

    # Add post data to the database
    cursor.execute(
        f'insert into posts values ("{post.id}", "{post.title}", "{post.author}", '
        f'"{post.selftext}", "{post.subreddit}", {subreddit_size}, {post.score}, '
        f'{post.upvote_ratio}, "{filename}", "{post.url}", {post.created_utc}, '
        '"False")'
    )
    connection.commit()

    print(f"[{pos_info[0]}/{pos_info[1]}] ARCHIVE: '{post.title}' successfully added to the "
          "archive.\n")


if __name__ == "__main__":
    print(SEPARATOR)

    # Run setup() if the config file does not exist.
    if not os.path.exists(DIR + "/config.json"):
        print("No data folder found, running setup...")
        setup()

    # Load secrets and connect to Reddit API.
    with open("config.json", mode='r') as f:
        secrets = json.loads(f.read())
    reddit = initialize_reddit_connection()

    # Initialize database connection
    connection, cursor = initialize_database_connection()

    # Separate initialization messages from main output
    print(SEPARATOR)

    archive_saved_posts(upvote=True)

    # Close database connection
    time.sleep(2)
    connection.close()
    print("SQLLite3: Database successfully closed.")
