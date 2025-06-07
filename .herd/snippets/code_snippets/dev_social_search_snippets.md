# Code Snippets from toollama/API/api-tools/tools/tools/tools2/dev_social_search.py

File: `toollama/API/api-tools/tools/tools/tools2/dev_social_search.py`  
Language: Python  
Extracted: 2025-06-07 05:25:30  

## Snippet 1
Lines 1-4

```Python
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
```

## Snippet 2
Lines 6-21

```Python
def __init__(self, username):
        self.username = str(username).strip()
        self.networks = {
            "facebook.com": "https://www.facebook.com/",
            "twitter.com": "https://twitter.com/",
            "instagram.com": "https://www.instagram.com/",
            "linkedin.com": "https://www.linkedin.com/in/",
            "github.com": "https://github.com/",
            "twitch.tv": "https://www.twitch.tv/",
            "reddit.com": "https://www.reddit.com/user/",
            "pinterest.com": "https://www.pinterest.com/",
            "tumblr.com": "https://www.tumblr.com/blog/view/",
            "flickr.com": "https://www.flickr.com/people/",
            "soundcloud.com": "https://soundcloud.com/",
            "snapchat.com": "https://www.snapchat.com/add/",
            "vimeo.com": "https://vimeo.com/",
```

## Snippet 3
Lines 22-29

```Python
"medium.com": "https://medium.com/@",
            "discord.com": "https://discord.com/users/",
            "steamcommunity.com": "https://steamcommunity.com/id/",
            "behance.net": "https://www.behance.net/",
            "dribbble.com": "https://dribbble.com/",
            "quora.com": "https://www.quora.com/profile/",
            "pixiv.net": "https://www.pixiv.net/en/users/",
            "open.spotify.com": "https://open.spotify.com/user/",
```

## Snippet 4
Lines 32-37

```Python
"clubhouse.com": "https://www.clubhouse.com/@",
            "epicgames.com": "https://www.epicgames.com/id/",
            "telegram.org": "https://t.me/",
            "rumble.com": "https://rumble.com/user/",
            "parler.com": "https://parler.com/user/",
            "gab.com": "https://gab.com/",
```

## Snippet 5
Lines 42-46

```Python
def check_account(self, network, base_url):
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = f"{base_url}{self.username}"
        try:
            response = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
```

## Snippet 6
Lines 48-51

```Python
if self.verify_account_exists(network, response):
                    return {"platform": network, "status": "Exists", "url": url}
                else:
                    return {"platform": network, "status": "Does not exist", "url": None}
```

## Snippet 7
Lines 83-85

```Python
elif network == "youtube.com":
            return "This channel does not exist." not in soup.text
        else:
```

## Snippet 8
Lines 92-99

```Python
for future in as_completed(future_to_network):
                network = future_to_network[future]
                try:
                    result = future.result()
                    self.results.append(result)
                except Exception as exc:
                    self.results.append({"platform": network, "status": "Error", "message": str(exc), "url": None})
```

## Snippet 9
Lines 105-110

```Python
def handler(args):
    username_to_check = args.input.username_to_check
    drummer = Drummer(username_to_check)
    drummer.check_accounts()
    return drummer.display_results()
```

## Snippet 10
Lines 118-120

```Python
FINAL aug 16 - being replaced -

    import requests
```

## Snippet 11
Lines 121-127

```Python
import logging
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
```

## Snippet 12
Lines 129-133

```Python
def __init__(self, username):
        self.username = str(username).strip()
        self.results = []
        self.platforms = self.get_platforms()
```

## Snippet 13
Lines 134-143

```Python
def get_platforms(self):
        # Extended list of platforms from Sherlock
        return {
            "GitHub": f"https://github.com/{self.username}",
            "Instagram": f"https://www.instagram.com/{self.username}/",
            "Twitter": f"https://twitter.com/{self.username}",
            "Facebook": f"https://www.facebook.com/{self.username}",
            "Reddit": f"https://www.reddit.com/user/{self.username}",
            "LinkedIn": f"https://www.linkedin.com/in/{self.username}",
            "Tumblr": f"https://{self.username}.tumblr.com",
```

## Snippet 14
Lines 148-163

```Python
"Medium": f"https://medium.com/@{self.username}",
            "Vimeo": f"https://vimeo.com/{self.username}",
            "SoundCloud": f"https://soundcloud.com/{self.username}",
            "Twitch": f"https://www.twitch.tv/{self.username}",
            "Dribbble": f"https://dribbble.com/{self.username}",
            "Behance": f"https://www.behance.net/{self.username}",
            "Flickr": f"https://www.flickr.com/people/{self.username}",
            "DeviantArt": f"https://www.deviantart.com/{self.username}",
            "Goodreads": f"https://www.goodreads.com/{self.username}",
            "GitLab": f"https://gitlab.com/{self.username}",
            "Bitbucket": f"https://bitbucket.org/{self.username}",
            "Steam": f"https://steamcommunity.com/id/{self.username}",
            "Patreon": f"https://www.patreon.com/{self.username}",
            "Ko-fi": f"https://ko-fi.com/{self.username}",
            "BuyMeACoffee": f"https://www.buymeacoffee.com/{self.username}",
            "AngelList": f"https://angel.co/{self.username}",
```

## Snippet 15
Lines 164-204

```Python
"ProductHunt": f"https://www.producthunt.com/@{self.username}",
            "500px": f"https://500px.com/{self.username}",
            "About.me": f"https://about.me/{self.username}",
            "WordPress": f"https://{self.username}.wordpress.com",
            "Blogspot": f"https://{self.username}.blogspot.com",
            "LiveJournal": f"https://{self.username}.livejournal.com",
            "VK": f"https://vk.com/{self.username}",
            "OK": f"https://ok.ru/{self.username}",
            "Weibo": f"https://weibo.com/{self.username}",
            "Douban": f"https://www.douban.com/people/{self.username}",
            "Zhihu": f"https://www.zhihu.com/people/{self.username}",
            "Quora": f"https://www.quora.com/profile/{self.username}",
            "Mix": f"https://mix.com/{self.username}",
            "Ello": f"https://ello.co/{self.username}",
            "Myspace": f"https://myspace.com/{self.username}",
            "Badoo": f"https://badoo.com/en/{self.username}",
            "Meetup": f"https://www.meetup.com/members/{self.username}",
            "Xing": f"https://www.xing.com/profile/{self.username}",
            "Kaggle": f"https://www.kaggle.com/{self.username}",
            "ResearchGate": f"https://www.researchgate.net/profile/{self.username}",
            "Academia": f"https://independent.academia.edu/{self.username}",
            "Scribd": f"https://www.scribd.com/{self.username}",
            "Slideshare": f"https://www.slideshare.net/{self.username}",
            "Scoop.it": f"https://www.scoop.it/u/{self.username}",
            "Disqus": f"https://disqus.com/by/{self.username}",
            "Gravatar": f"https://en.gravatar.com/{self.username}",
            "Keybase": f"https://keybase.io/{self.username}",
            "Last.fm": f"https://www.last.fm/user/{self.username}",
            "Bandcamp": f"https://bandcamp.com/{self.username}",
            "ReverbNation": f"https://www.reverbnation.com/{self.username}",
            "Mixcloud": f"https://www.mixcloud.com/{self.username}",
            "8tracks": f"https://8tracks.com/{self.username}",
            "Audiomack": f"https://audiomack.com/{self.username}",
            "DatPiff": f"https://www.datpiff.com/profile/{self.username}",
            "Gumroad": f"https://gumroad.com/{self.username}",
            "Payhip": f"https://payhip.com/{self.username}",
            "Teespring": f"https://teespring.com/stores/{self.username}",
            "Redbubble": f"https://www.redbubble.com/people/{self.username}",
            "Society6": f"https://society6.com/{self.username}",
            "Zazzle": f"https://www.zazzle.com/{self.username}",
            "CafePress": f"https://www.cafepress.com/profile/{self.username}",
```

## Snippet 16
Lines 205-211

```Python
"Threadless": f"https://www.threadless.com/@{self.username}",
            "DesignByHumans": f"https://www.designbyhumans.com/shop/{self.username}",
            "Spreadshirt": f"https://www.spreadshirt.com/user/{self.username}",
            "Storenvy": f"https://{self.username}.storenvy.com",
            "BigCartel": f"https://{self.username}.bigcartel.com",
            "Etsy": f"https://www.etsy.com/shop/{self.username}",
            "ArtStation": f"https://www.artstation.com/{self.username}"
```

## Snippet 17
Lines 215-217

```Python
logging.info(f"Checking {platform_name} for username '{self.username}' at {url}")
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
```

## Snippet 18
Lines 220-223

```Python
if self.username in response.text:
                        self.results.append({"platform": platform_name, "status": "Exists", "url": url})
                    else:
                        self.results.append({"platform": platform_name, "status": "Does not exist", "url": None})
```

## Snippet 19
Lines 227-230

```Python
if username_element and username_element.get('content') and self.username in username_element['content']:
                        self.results.append({"platform": platform_name, "status": "Exists", "url": url})
                    else:
                        self.results.append({"platform": platform_name, "status": "Does not exist", "url": None})
```

## Snippet 20
Lines 235-238

```Python
except requests.exceptions.RequestException as e:
            logging.error(f"Error checking {platform_name}: {e}")
            self.results.append({"platform": platform_name, "status": "Error", "message": str(e), "url": None})
```

## Snippet 21
Lines 242-245

```Python
for future in as_completed(future_to_platform):
                platform = future_to_platform[future]
                try:
                    result = future.result()
```

## Snippet 22
Lines 261-264

```Python
if not hasattr(args, 'input'):
        logging.error("Error: args does not have an 'input' attribute.")
        return {"message": "Invalid input structure: 'input' attribute missing.", "results": []}
```

## Snippet 23
Lines 265-268

```Python
if args.input is None:
        logging.error("Error: args.input is None.")
        return {"message": "Invalid input structure: 'input' is None.", "results": []}
```

## Snippet 24
Lines 271-277

```Python
elif hasattr(args.input, '__dict__'):
        input_dict = vars(args.input)
    else:
        logging.error("Error: args.input is of an unsupported type: %s", type(args.input))
        return {"message": f"Invalid input structure: expected dict, got {type(args.input)}.", "results": []}

    username_to_check = input_dict.get("username_to_check")
```

## Snippet 25
Lines 278-284

```Python
if not username_to_check:
        logging.error("Error: Username is required.")
        return {"message": "Username is required.", "results": []}

    drummer = SherlockDrummer(username_to_check)
    drummer.check_accounts()
    return drummer.display_results()
```

