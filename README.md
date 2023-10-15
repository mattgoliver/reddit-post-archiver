# reddit-post-archiver

'secrets.json' must be in the following format to allow for PRAW initialization (without the outer pair of quotation marks):\
"{
  "client_id": "clientID",
  "client_secret": "clientSecret",
  "username": "username",
  "password": "password",
  "user_agent": "userAgent"
}"\
From [PRAW's Quick Start Guide](https://praw.readthedocs.io/en/stable/getting_started/quick_start.html):\
If you don’t already have a client ID and client secret, follow [Reddit’s First Steps Guide](https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example#first-steps) to create them.\
A user agent is a unique identifier that helps Reddit determine the source of network requests. To use Reddit’s API, you need a unique and descriptive user agent. Read more about user agents at [Reddit’s API wiki page](https://github.com/reddit-archive/reddit/wiki/API).
