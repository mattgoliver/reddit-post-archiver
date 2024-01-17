"""Reddit Post Archiver.

Author: Matthew Oliver
Version: 1/17/2024
"""
import access  # Allows for accessing the post/archive database
import random  # Allows for random file names
import json  # Allows access to the .json login information file
import praw  # Allows access to Reddit's API
import sqlite3  # Allows for database management
import os  # Allows for checking if database exists
import uuid  # Allows for generation of unique file names
import urllib.request  # Allows for media downloading
import requests  # Allows for retrieval of media type given URL
import mimetypes  # Allows for retrieval of media type given URL
import time
import sys


DIR = os.getcwd()
DATABASE_NAME = "reddit-post-archive.sqlite3"
SEPARATOR = '-' * 80


# Initialization functions
def setup():
    """Creates the file structure and config file."""
    try:
        os.mkdir(DIR + "/data")
    except FileExistsError:
        print("Data folder found.")

    config = dict()

    config["REDDIT_CREDENTIALS"] = {"client_id": "", "client_secret": "", "username": "", "password": "", "user_agent": ""}
    config["DOWNLOAD"] = {"video_extensions": []}

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
    cursor.execute(f"select * from downloads where id='{post_id}'")
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

        print()  # Improve output readability, puts spaces in between the output of each post

        if check_duplicate(post.id):
            print(f"[{pos_info[0]}/{pos_info[1]}] Duplicate found: {post.title}")
            if unsave:
                post.unsave()
            continue

        # Download file and save the filename of the downloaded file
        filename = download(post)

        # Continue to next post if there was no file to download
        if filename is None:
            print(f"[{pos_info[0]}/{pos_info[1]}] Empty post found: {post.title}")
            if unsave:
                post.unsave()
            continue

        # Add the downloaded file to the database
        archive(post, filename)

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


def download(post, log=False):
    """Downloads post at given url.

    Args:
          post: Post to download.
          log (bool): Print log messages, default = False

    Returns:
         tup: File name
    """
    file_name = ""
    url = post.url

    # Retrieve file type
    response = requests.get(url)
    content_type = response.headers['content-type']
    file_type = mimetypes.guess_extension(content_type)

    # Return None if there is no file to download
    if file_type is None:
        print(f"DOWNLOAD: Error with post: '{post.title}', no media to download.")
        return None

    print(f"DOWNLOAD: Downloading post: '{post.title}', file type: '{file_type}'.")

    # Loop until unique file name is generated
    post_exists = True
    while post_exists is True:
        file_name = "./media/" + str(uuid.uuid4().hex) + file_type

        if not os.path.isfile(file_name):  # Check if file name already exists
            post_exists = False

    # Download file
    urllib.request.urlretrieve(url, file_name)

    return file_name


def archive(post, file_name, log=False):
    """Archives the post at the given url.

    Information archived: ID, title, author, content (text & media), subreddit, url, date, amount and ratio of upvotes

    Args:
        post: Post to archive.
        file_name: Name of downloaded file to associate post information with.
        log (bool): Print log messages, default = False
    """
    # Find the subscriber count of the post's subreddit
    subreddit_size = int(reddit.subreddit(str(post.subreddit)).subscribers)

    if log:
        print(f"ARCHIVE: ID: {post.id}, Title: {post.title}, Author: {post.author}, Text: {post.selftext}, "
              f"Subreddit: {post.subreddit}, Subreddit Size: {subreddit_size}, Upvotes: {post.score}, "
              f"Ratio: {post.upvote_ratio}, File name: {file_name}, URL: {post.url}, Created: {post.created_utc}")

    # Add post data to the database
    cursor.execute(
        f"insert into posts values ('{post.id}', '{post.title}', '{post.author}', '{post.selftext}', "
        f"'{post.subreddit}', {subreddit_size}, {post.score}, {post.upvote_ratio}, '{file_name}', '{post.url}', "
        f"{post.created_utc})"
    )
    connection.commit()

    print(f"ARCHIVE: '{post.title}' successfully added to the archive.")


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

    archive_saved_posts(limit=2)

    # Close database connection
    time.sleep(2)
    connection.close()
    print("SQLLite3: Database successfully closed.")

    """archive_saved_posts(limit=10)"""
