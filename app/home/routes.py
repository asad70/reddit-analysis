# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import time
from flask.globals import request
from app.home import blueprint
from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app import login_manager
from jinja2 import TemplateNotFound
from flask import jsonify
import matplotlib.pyplot as plt
import nltk
import pandas as pd
import praw
import squarify
from flask import Flask, render_template
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os
from app.settings import APP_STATIC
from data import *
from app.base.models import User, Picks
from app import db

nltk.download('stopwords')
set(stopwords.words('english'))


@blueprint.route('/index')
#@login_required
def index1():
    return render_template('core/reddit-index.html')

@blueprint.route('/index1')
#@login_required
def index():
    # db.drop_all()
    # db.create_all()
    #found=Picks.query.all()
    arr=[]
    for i in Picks.query.all():
        print(i.__dict__)
        temp = i
        #temp.time = int(time.mktime(temp.time.timetuple())) * 1000
        del temp._sa_instance_state
        arr.append(temp.__dict__)
        
    return render_template('index.html', time=12345, df=arr)


@blueprint.route('/reddit-index')
def my_form():
    return render_template('core/reddit-index.html')



@blueprint.route('/reddit-index', methods=['POST'])
def my_form_input():
    input = {
        'subs':  request.form['subs'] if request.form['subs'] else ['wallstreetbets'],
        'post_flairs': request.form['post_flairs'] if request.form['post_flairs'] else {'Daily Discussion', 'Weekend Discussion', 'Discussion'},
        'goodAuth': request.form['goodAuth'] if request.form['goodAuth'] else{'AutoModerator'},
        'uniqueCmt': request.form['uniqueCmt'] if request.form['uniqueCmt'] else True,
        'ignoreAuthP': request.form['ignoreAuthP'] if request.form['ignoreAuthP'] else {'example'},
        'ignoreAuthC': request.form['ignoreAuthC'] if request.form['ignoreAuthC'] else {'example,'},
        'upvoteRatio': request.form['upvoteRatio'] if request.form['upvoteRatio'] else 0.70,
        'ups': request.form['ups'] if request.form['ups'] else 20,
        'limit': request.form['limit'] if request.form['limit'] else 500,
        'upvotes': request.form['upvotes'] if request.form['upvotes'] else 2,
        'picks': request.form['picks'] if request.form['picks'] else 10,
        'picks_ayz': request.form['picks_ayz'] if request.form['picks_ayz'] else 5,
    }
    print("input is", input)

    return render_template('core/reddit-index.html')


@ blueprint.route('/data', methods=['POST', 'GET'])
def my_form_post():
    import time
    start_time = time.time()
    ctime = time.ctime()
    print('time is', time.ctime())

    reddit = praw.Reddit(user_agent="Comment Extraction",
                         client_id="ZM9jcd0nyXvtlA",
                         client_secret="2WjTo27fw6c98-x0Nb5oTICNB-6D0g",
                         username="",
                         password="")
    '''############################################################################'''
    # set the program parameters
    subs = ['wallstreetbets']     # sub-reddit to search
    # posts flairs to search || None flair is automatically considered
    post_flairs = {'Daily Discussion', 'Weekend Discussion', 'Discussion'}
    # authors whom comments are allowed more than once
    goodAuth = {'AutoModerator'}
    uniqueCmt = True                # allow one comment per author per symbol
    ignoreAuthP = {'example'}       # authors to ignore for posts
    ignoreAuthC = {'example'}       # authors to ignore for comment
    upvoteRatio = 0.70         # upvote ratio for post to be considered, 0.70 = 70%
    ups = 20       # define # of upvotes, post is considered if upvotes exceed this #
    limit = 5     # define the limit, comments 'replace more' limit
    upvotes = 2     # define # of upvotes, comment is considered if upvotes exceed this #
    picks = 10     # define # of picks here, prints as "Top ## picks are:"
    picks_ayz = 5   # define # of picks for sentiment analysis
    '''############################################################################'''

    posts, count, c_analyzed, tickers, titles, a_comments = 0, 0, 0, {}, [], {}
    cmt_auth = {}
    num = 0
    comm = 0
    for sub in subs:
        subreddit = reddit.subreddit(sub)
        hot_python = subreddit.hot()    # sorting posts by hot
        # Extracting comments, symbols from subreddit
        print("running", str(hot_python))
        for submission in hot_python:
            flair = submission.link_flair_text
            author = submission.author.name

            # custom write func
            file = open(os.path.join(APP_STATIC, "output/sample.py"),
                        "w", encoding='utf-8')
            hotlist = [i for i in hot_python]
            file.write("start time was %s num is %d and hotlist is %s " %
                       (str(time.ctime()), num, str(hotlist)))
            print('num is', num)
            file.close()
            num += 1

            # checking: post upvote ratio # of upvotes, post flair, and author
            if submission.upvote_ratio >= upvoteRatio and submission.ups > ups and (flair in post_flairs or flair is None) and author not in ignoreAuthP:
                submission.comment_sort = 'new'
                comments = submission.comments
                titles.append(submission.title)
                posts += 1
                try:
                    submission.comments.replace_more(limit=limit)
                    for comment in comments:
                        file = open(os.path.join(
                            APP_STATIC, "output/sample.py"), "a", encoding='utf-8')
                        file.write("comnum is %d and comm is %s " %
                                   (comm, str(comment)))
                        file.close()
                        comm += 1
                        #print("comnum is", comm)
                        # try except for deleted account?
                        try:
                            auth = comment.author.name
                        except:
                            pass
                        c_analyzed += 1

                        # checking: comment upvotes and author
                        if comment.score > upvotes and auth not in ignoreAuthC:
                            split = comment.body.split(" ")
                            for word in split:
                                word = word.replace("$", "")
                                # upper = ticker, length of ticker <= 5, excluded words,
                                if word.isupper() and len(word) <= 5 and word not in blacklist and word in us:

                                    # unique comments, try/except for key errors
                                    if uniqueCmt and auth not in goodAuth:
                                        try:
                                            if auth in cmt_auth[word]:
                                                break
                                        except:
                                            pass

                                    # counting tickers
                                    if word in tickers:
                                        tickers[word] += 1
                                        a_comments[word].append(comment.body)
                                        cmt_auth[word].append(auth)
                                        count += 1
                                    else:
                                        tickers[word] = 1
                                        cmt_auth[word] = [auth]
                                        a_comments[word] = [comment.body]
                                        count += 1
                except Exception as e:
                    print(e)

    # sorts the dictionary
    symbols = dict(
        sorted(tickers.items(), key=lambda item: item[1], reverse=True))
    top_picks = list(symbols.keys())[0:picks]
    time = (time.time() - start_time)

    # print top picks
    print("It took {t:.2f} seconds to analyze {c} comments in {p} posts in {s} subreddits.\n".format(
        t=time, c=c_analyzed, p=posts, s=len(subs)))
    print("Posts analyzed saved in titles")
    # for i in titles: print(i)  # prints the title of the posts analyzed

    print(f"\n{picks} most mentioned picks: ")
    times = []
    top = []
    for i in top_picks:
        print(f"{i}: {symbols[i]}")
        times.append(symbols[i])
        top.append(f"{i}: {symbols[i]}")

    # Applying Sentiment Analysis
    scores, s = {}, {}

    vader = SentimentIntensityAnalyzer()
    # adding custom words from data.py
    vader.lexicon.update(new_words)

    picks_sentiment = list(symbols.keys())[0:picks_ayz]

    for symbol in picks_sentiment:
        stock_comments = a_comments[symbol]
        for cmnt in stock_comments:
            score = vader.polarity_scores(cmnt)
            if symbol in s:
                s[symbol][cmnt] = score
            else:
                s[symbol] = {cmnt: score}
            if symbol in scores:
                for key, _ in score.items():
                    scores[symbol][key] += score[key]
            else:
                scores[symbol] = score

        # calculating avg.
        for key in score:
            scores[symbol][key] = scores[symbol][key] / symbols[symbol]
            scores[symbol][key] = "{pol:.3f}".format(pol=scores[symbol][key])

    picksdb = Picks(pick=scores)
    timesdb = Picks(pick=[times, top, top_picks])
    # print(picks)
    db.session.add(picksdb)
    db.session.add(timesdb)
    db.session.commit()
    # printing sentiment analysis
    print(f"\nSentiment analysis of top {picks_ayz} picks:")
    df = pd.DataFrame(scores)
    df.index = ['Bearish', 'Neutral', 'Bullish', 'Total/Compound']
    df = df.T
    print(df)

    # Date Visualization
    # most mentioned picks
    squarify.plot(sizes=times, label=top, alpha=.7)
    plt.axis('off')
    plt.title(f"{picks} most mentioned picks")
    # plt.show()

    # Sentiment analysis
    df = df.astype(float)
    colors = ['red', 'springgreen', 'forestgreen', 'coral']
    df.plot(kind='bar', color=colors,
            title=f"Sentiment analysis of top {picks_ayz} picks:")
    # plt.show()
    print('done')
    file = open(os.path.join(APP_STATIC, "output/final_output.py"),
                "w", encoding='utf-8')
    file.write("start time was %s /n/n top picks are %s and df is %s" %
               (str(ctime), str(top_picks), str(df)))
    print('num is', num)
    file.close()

    return render_template('core/reddit-data.html', result='done', final=df, t=ctime, c=c_analyzed, p=posts, s=len(subs))


@ blueprint.route('/visualize', methods=['POST', 'GET'])
def visualize():
    return render_template('core/reddit-data.html', result='done', final='ok')


@ blueprint.route('/status_bar', methods=['POST', 'GET'])
def status_bar():
    file = open(os.path.join(APP_STATIC, "output/sample.py"), "r")
    stat = file.read()
    file.close()
    admin = User(username='admin', email='admin@example.com', password='pass')
    db.session.add(admin)
    print(User.query.all())
    return render_template('core/reddit-data.html', final=stat, result='read complete')


@ blueprint.route('/output', methods=['POST', 'GET'])
def output():
    file = open(os.path.join(APP_STATIC, 'output/final_output.py'), "r")
    stat = file.read()
    print("stat is %s" % stat)
    file.close()
    return render_template('core/reddit-output.html', arg=stat)


@ blueprint.route('/test', methods=['POST', 'GET'])
def test():
    picks = Picks(pick='hoho', bearish='whooter', bullish='what')
    db.session.add(picks)
    db.session.commit()
    return jsonify({'result': 'ohk'})


@ blueprint.route('/test2', methods=['POST', 'GET'])
def test2():
    hoho = 'hoho'
    found=Picks.query.filter_by(pick='hoho').first()
    print((Picks.query.filter_by(pick='hoho').first()))
    return 'ohkk'

@ blueprint.route('/core/settings', methods=['GET'])
def settingsGet():
    return render_template('core/settings.html',delete_db=delete_db, create_db=create_db)

@ blueprint.route('/core/settings', methods=['POST'])
def settings():
    query = request.form['query']
    found = Picks.query.filter_by(id=query).first()
    print(found)
    return render_template('core/settings.html', found=found, delete_db=delete_db, create_db=create_db)
def delete_db():
    #db.drop_all()
    return 'DB deleted'
def create_db():
    db.create_all()
    return 'All DB created'




@ blueprint.route('/core/<template>')
def route_core_template(template):
    try:
        if not template.endswith('.html'):
            core='core/'
            template += '.html'
            template=core+template
        return render_template(template)
    except TemplateNotFound:
        return render_template('page-404.html'), 404
    except:
        return render_template('page-500.html'), 500

@ blueprint.route('/<template>')
def route_template(template):
    try:
        if not template.endswith('.html'):
            template += '.html'
        return render_template(template)
    except TemplateNotFound:
        return render_template('page-404.html'), 404
    except:
        return render_template('page-500.html'), 500
