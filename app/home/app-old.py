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
from settings import APP_STATIC

nltk.download('stopwords')

set(stopwords.words('english'))

app = Flask(__name__)


@app.route('/')
def my_form():
    return render_template('form.html')


@app.route('/data', methods=['POST', 'GET'])
def my_form_post():
    import time
    start_time = time.time()
    ctime=time.ctime()
    print('time is', time.ctime())

    reddit = praw.Reddit(user_agent="Comment Extraction",
    client_id="ZM9jcd0nyXvtlA",
    client_secret="2WjTo27fw6c98-x0Nb5oTICNB-6D0g",        
    username="",
    password="")
    '''############################################################################'''
    # set the program parameters
    subs = ['wallstreetbets' ]     # sub-reddit to search
    post_flairs = {'Daily Discussion', 'Weekend Discussion', 'Discussion'}    # posts flairs to search || None flair is automatically considered
    goodAuth = {'AutoModerator'}   # authors whom comments are allowed more than once
    uniqueCmt = True                # allow one comment per author per symbol
    ignoreAuthP = {'example'}       # authors to ignore for posts 
    ignoreAuthC = {'example'}       # authors to ignore for comment 
    upvoteRatio = 0.70         # upvote ratio for post to be considered, 0.70 = 70%
    ups = 20       # define # of upvotes, post is considered if upvotes exceed this #
    limit = 500     # define the limit, comments 'replace more' limit
    upvotes = 2     # define # of upvotes, comment is considered if upvotes exceed this #
    picks = 10     # define # of picks here, prints as "Top ## picks are:"
    picks_ayz = 5   # define # of picks for sentiment analysis
    '''############################################################################'''


    posts, count, c_analyzed, tickers, titles, a_comments = 0, 0, 0, {}, [], {}
    cmt_auth = {}
    num=0
    comm=0
    for sub in subs:
        subreddit = reddit.subreddit(sub)
        hot_python = subreddit.hot()    # sorting posts by hot
        # Extracting comments, symbols from subreddit
        print("running", str(hot_python))
        for submission in hot_python:
            flair = submission.link_flair_text 
            author = submission.author.name
            
            #custom write func
            file = open(os.path.join(APP_STATIC, "output/sample.py"), "w", encoding='utf-8')
            hotlist = [i for i in hot_python]
            file.write("start time was %s num is %d and hotlist is %s " %(str(time.ctime()), num, str(hotlist)))
            print('num is', num)
            file.close()         
            num+=1

            # checking: post upvote ratio # of upvotes, post flair, and author 
            if submission.upvote_ratio >= upvoteRatio and submission.ups > ups and (flair in post_flairs or flair is None) and author not in ignoreAuthP:   
                submission.comment_sort = 'new'     
                comments = submission.comments
                titles.append(submission.title)
                posts += 1
                try: 
                    submission.comments.replace_more(limit=limit)   
                    for comment in comments:
                        file = open(os.path.join(APP_STATIC, "output/sample.py"), "a", encoding='utf-8')
                        file.write("comnum is %d and comm is %s " %(comm, str(comment)))
                        file.close()         
                        comm+=1
                        print("comnum is", comm)
                        # try except for deleted account?
                        try: auth = comment.author.name
                        except: pass
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
                                            if auth in cmt_auth[word]: break
                                        except: pass
                                        
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
                except Exception as e: print(e)
                
                        

    # sorts the dictionary
    symbols = dict(sorted(tickers.items(), key=lambda item: item[1], reverse = True))
    top_picks = list(symbols.keys())[0:picks]
    time = (time.time() - start_time)

    # print top picks
    print("It took {t:.2f} seconds to analyze {c} comments in {p} posts in {s} subreddits.\n".format(t=time, c=c_analyzed, p=posts, s=len(subs)))
    print("Posts analyzed saved in titles")
    #for i in titles: print(i)  # prints the title of the posts analyzed


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
                s[symbol] = {cmnt:score}      
            if symbol in scores:
                for key, _ in score.items():
                    scores[symbol][key] += score[key]
            else:
                scores[symbol] = score
                
        # calculating avg.
        for key in score:
            scores[symbol][key] = scores[symbol][key] / symbols[symbol]
            scores[symbol][key]  = "{pol:.3f}".format(pol=scores[symbol][key])
    
    # printing sentiment analysis 
    print(f"\nSentiment analysis of top {picks_ayz} picks:")
    df = pd.DataFrame(scores)
    df.index = ['Bearish', 'Neutral', 'Bullish', 'Total/Compound']
    df = df.T
    print(df)

    # Date Visualization
    # most mentioned picks    
    squarify.plot(sizes=times, label=top, alpha=.7 )
    plt.axis('off')
    plt.title(f"{picks} most mentioned picks")
    #plt.show()

    # Sentiment analysis
    df = df.astype(float)
    colors = ['red', 'springgreen', 'forestgreen', 'coral']
    df.plot(kind = 'bar', color=colors, title=f"Sentiment analysis of top {picks_ayz} picks:")
    #plt.show()
    print('done')
    file = open(os.path.join(APP_STATIC, "output/final_output.py"), "w", encoding='utf-8')
    file.write("start time was %s /n/n top picks are %s and df is %s" %(str(ctime), str(top_picks), str(df)))
    print('num is', num)
    file.close()  

    return render_template('data.html', result='done', final=df, t=ctime, c=c_analyzed, p=posts, s=len(subs))


@app.route('/visualize', methods=['POST', 'GET'])
def visualize():
    return render_template('data.html', result='done', final='ok')

@app.route('/status_bar', methods=['POST', 'GET'])
def status_bar():
    file = open(os.path.join(APP_STATIC, "output/sample.py"), "r")
    stat = file.read()
    file.close()  
    return render_template('data.html', final=stat, result='read complete')

@app.route('/output', methods=['POST', 'GET'])
def output():
    file = open(os.path.join(APP_STATIC, 'output/final_output.py'), "r")
    stat = file.read()
    file.close()  
    return render_template('output.html', arg=stat)

if __name__ == "__main__":
    app.run(debug=False, port=4700, threaded=True)
