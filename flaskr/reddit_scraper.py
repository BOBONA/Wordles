import os
import re

import praw
from requests import request

LINK_REGEX = r'(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])'
url_regex = re.compile(LINK_REGEX, re.MULTILINE)


def authorize(client_id, client_secret):
    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent='WordlesDataScraper')


def scrape_submissions(reddit, submissions, blacklist):
    urls = set()
    wordles = []
    last_fetched = 0
    crossposts = []
    data = reddit.info(fullnames=submissions)
    for submission in data:
        if not submission.id:
            continue
        data = submission.title + submission.selftext
        if not submission.is_self:
            data += ' ' + submission.url
        match = re.search(url_regex, data)
        if match:
            url = normalize_url(match.group())
            if is_wordle_url(url, blacklist) and url not in urls:
                urls.add(url)
                stripped = ''.join(data.split())[:100]  # remove whitespace from data
                wordles.append({'url': url, 'data': stripped, 'date': submission.created_utc})
        if submission.url.startswith('/r/'):
            crossposts.append('t3_' + submission.url.split('/')[4])
        last_fetched = submission.created_utc
    if len(crossposts):
        crosspost_results = scrape_submissions(reddit, crossposts, blacklist)[0]
        for crosspost in crosspost_results:
            if crosspost['url'] not in urls:
                wordles.append(crosspost)
                urls.add(crosspost['url'])
    return wordles, last_fetched


def normalize_url(url):
    if url.endswith('/'):
        url = url[:-1]  # remove trailing /
    i = url.find('#')
    if i != -1:
        url = url[:i]  # remove trailing #links
    parts = url.split('/')
    if parts[2].startswith('www.'):
        parts[2] = parts[2][4:]
        url = '/'.join(parts)
    return url


def is_wordle_url(url, blacklist):
    parts = url.split('/')
    if parts[2] in blacklist:  # has invalid site
        return False
    if '.' in parts[-1] and len(parts) > 3:  # url is to a file
        return False
    for part in parts:
        if len(part) > 20:
            return False
    return 'le' in url


def retrieve_submission_ids(subreddit, after):
    res = request('GET', 'https://api.pushshift.io/reddit/submission/search',
                  params={'subreddit': subreddit, 'after': after,
                          'sort_type': 'created_utc', 'sort': 'asc', 'fields': 'id', 'size': '100'})
    return ['t3_' + obj['id'] for obj in res.json()['data']]


if __name__ == '__main__':
    r = authorize(os.environ.get('REDDIT_ID'), os.environ.get('REDDIT_SECRET'))
    date = int(r.subreddit('wordle').created_utc)
    ids = retrieve_submission_ids('wordle', date)
    with open('wordle_url_blacklist.txt', 'r') as file:
        black = file.read().splitlines()
    scrape_submissions(r, ids, black)
