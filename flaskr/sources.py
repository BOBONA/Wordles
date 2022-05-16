import flaskr.reddit_scraper as scraper

from flaskr.models import Wordle


def from_reddit(source, session, config, blacklist):
    ids = [None]  # is there a better way to do this...
    while len(ids):
        ids = scraper.retrieve_submission_ids(source.name, source.last_fetched)
        if len(ids):
            reddit = scraper.authorize(config['REDDIT_ID'], config['REDDIT_SECRET'])
            wordles, last_fetched = scraper.scrape_submissions(reddit, ids, blacklist)
            source.last_fetched = last_fetched
            for wordle in wordles:
                if not Wordle.query.filter(Wordle.url == wordle['url']).first():
                    session.add(Wordle(wordle['url'], wordle['data'], wordle['date'], source.id))
            session.commit()
            print(last_fetched)


def get(source):
    if source in sources:
        return sources[source]
    else:
        return lambda *args: None


sources = {'reddit': from_reddit}
