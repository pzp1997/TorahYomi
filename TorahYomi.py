#!/usr/bin/env python2.7

"""
TorahYomi.py
Copyright 2015, Palmer Paul

Twitter bot that tweets one word of the Torah
roughly every hour (2926 seconds, to be precise).
It will take 7 years and 5 months to finish
the entire Torah, exactly the same amount of time
that it takes to complete Daf Yomi.
"""

from urllib2 import urlopen
import json
from TwitterFollowBot import TwitterBot
# import tweepy

__author__ = 'Palmer Paul'
__version__ = '1.0.0'
__email__ = 'pzpaul2002@yahoo.com'

books = ['Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy']
# [book['title'] for book in
# req_to_sefaria('/index')[0]['contents'][0]['contents']]

book_lengths = {
    'Genesis': 50,
    'Exodus': 40,
    'Leviticus': 27,
    'Numbers': 36,
    'Deuteronomy': 34
}
# {book:req_to_sefaria('/index/{}'.format(book))['length'] for book in books}


def req_to_sefaria(node):
    """Makes a request to the Sefaria Torah Texts API"""
    BASE_URL = 'http://www.sefaria.org/api'
    return json.loads(urlopen(BASE_URL + node).read())


def get_chapter(book, chapter_num):
    """Gets chapter specified by ``book`` and ``chapter_num`` from Sefaria"""
    req = req_to_sefaria('/texts/{}.{}?context=0&commentary=0'.format(
        book, chapter_num))
    words = ' '.join(req['he']).split()

    # filters out non-words
    words = [word for word in words if word not in
             (u'(\u05e4)', u'\u05c0', u'(\u05e1)')]
    words.append((book, chapter_num))
    return words


def save_words_to_cache(words):
    """Saves list of words to ``CACHE_NAME``"""
    CACHE_NAME = 'TorahYomiCache.txt'
    with open(CACHE_NAME, 'w') as file_pointer:
        json.dump(words, file_pointer)


def read_cache():
    """Returns contents of cache or empty list if cache doesn't exist"""
    CACHE_NAME = 'TorahYomiCache.txt'

    try:
        with open(CACHE_NAME, 'r') as file_pointer:
            return json.load(file_pointer)
    except (IOError, ValueError):
        with open(CACHE_NAME, 'w') as file_pointer:
            return []

def tweet(msg):
    my_bot = TwitterBot()
    my_bot.send_tweet(msg)

'''
def tweet(msg):
    """Authenticates and sends a tweet with content ``msg``"""
    with open('SECRETS', 'r') as file_pointer:
        tokens = file_pointer.read().splitlines()

    auth = tweepy.OAuthHandler(*tokens[:2])
    auth.set_access_token(*tokens[2:])

    api = tweepy.API(auth)
    api.update_status(msg)
'''


def main():
    cache = read_cache()

    if len(cache) < 2:
        try:
            book, chapter_num = cache[-1]

            if book_lengths[book] > chapter_num:
                # starts a new chapter
                chapter_num += 1
            else:
                # starts a new book
                book = books[(books.index(book) + 1) % 5]
                chapter_num = 1

                # tweets Chazak Chazak V'nitchazek when a book is finished
                tweet(u'\u05d7\u05b2\u05d6\u05b7\u05e7 '  # Chazak
                      u'\u05d7\u05b2\u05d6\u05b7\u05e7 '  # Chazak
                      u'\u05d5\u05e0\u05ea\u05d7\u05d6\u05e7')  # V'nitchazek

        except IndexError:
            book, chapter_num = 'Genesis', 1
        cache = get_chapter(book, chapter_num)
    tweet(unicode(cache.pop(0)).encode('utf-8'))
    save_words_to_cache(cache)


if __name__ == '__main__':
    main()
