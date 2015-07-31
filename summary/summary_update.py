from conn_db import conn_DB
from namedlist import namedlist
from summarizer import summarize
from comment_select import *

import sys
import argparse
import datetime
import math
import nltk
import re

#TODO: reconsider period

CommentInfo = namedlist('CommentInfo','cid,sentence,rating')
SENT_TOKENIZER = nltk.data.load('tokenizers/punkt/english.pickle')
PERCENT = 0.4
LEAST = 5
SHORTEST = 100
SENTIMENT = ['negative','positive']

def summary_update(db, cur, tid, period, portion):
    current = datetime.datetime.now()
    last = current - datetime.timedelta(hours=period)
    last = last.strftime("%Y-%m-%d %H:%M:%S")
    print last
    get_entities = "SELECT eid FROM entity where tid="+tid+" AND updated>'"+last+"';"
    print get_entities
    cur.execute(get_entities)
    entities = cur.fetchall()
    counter = 1
    for entity in entities:
        print counter
        print entity[0]
        deletion = "DELETE summary.* FROM comment INNER JOIN summary ON comment.cid=summary.cid WHERE eid="+str(entity[0]);
        print deletion
        cur.execute(deletion)
        get_comments = ["SELECT cid,body,sentiment FROM comment where eid="
                +str(entity[0])+" AND sentiment<0;",
                "SELECT cid,body,sentiment FROM comment where eid="
                +str(entity[0])+" AND sentiment>0;"]
        for i in xrange(0,len(get_comments)):
            query = get_comments[i]
            print query
            cur.execute(query)
            comment_list = []
            comment_set = set([])
            for c,s,r in cur.fetchall():
                count = len(comment_set)
                # MetaFilter comments have html labels, get rid of them
                if tid == '1':
                    s = s.replace('\\n','')
                    s = re.sub('<[^<]+?>','',s)
                # Convert to unicode
                s = s.decode('utf8')
                # Get rid of duplicate comments
                if len(set(nltk.word_tokenize(s))) > 5:
                    comment_set.add(s)
                if count != len(comment_set):
                    comment_list.append(CommentInfo(c,s,r))
            # If total number of comments is too small, no need to pick representatives
            if len(comment_list) < LEAST:
                represent = comment_list
            else:
                num = int(math.ceil(portion*len(comment_list)))
                num = max(LEAST,num)
                num = min(100,num)
                represent = sentiment(SENTIMENT[i],comment_list,num)

            for i in xrange(0,len(represent)):
                comment = represent[i].sentence
                word_list = nltk.word_tokenize(comment)
                sentence_list = SENT_TOKENIZER.tokenize(comment)
                # Do summarization only if original comment is not short
                if len(word_list) > SHORTEST:
                    num = int(math.ceil(PERCENT*len(sentence_list)))
                    summary = summarize(comment,num,'lsa')
                    print "lsa: " + summary
                    insert_summary = 'INSERT INTO summary(cid,rank,mid,body) VALUES('+str(represent[i].cid)+','+str(i+1)+','+str(3)+',"'+summary+'");'
                    #print insert_summary
                    cur.execute(insert_summary)
                    summary = summarize(comment,num,'textrank')
                    print "textrank: " + summary
                    insert_summary = 'INSERT INTO summary(cid,rank,mid,body) VALUES('+str(represent[i].cid) + ','+str(i+1)+','+str(4)+',"'+summary+'");'
                    #print insert_summary
                    cur.execute(insert_summary)
                else:
                    comment = comment.replace("\\","").replace("\"","\"\"")
                    insert_original = 'INSERT INTO summary(cid,rank,mid,body) VALUES('+str(represent[i].cid) + ','+str(i+1)+','+str(5)+',"'+comment+'");'
                    print "original: " + comment
                    cur.execute(insert_original)

        counter += 1
        #db.commit()


def _arg_parser():
    parser = argparse.ArgumentParser(description='A script to generate summaries for each entity and write into database.\nEx: python summary_generator.py --ini=db.ini --db=weiss')
    parser.add_argument('--ini', dest='ini', action='store', help='The configuration filename, where you store your username, password, hostname and database you want to use', required=True)
    parser.add_argument('--db', dest='db', action='store', help='The name of the database you want to connect', required=True)
    parser.add_argument('--tid', dest='tid', action='store', help='tid:1 news, tid:2 restaurant, tid:3 movie', required=True)

    results = parser.parse_args()

    ini_file = results.ini
    db_name = results.db
    tid = results.tid

    return (ini_file, db_name, tid)


def main():
    ini_file, db_name, tid = _arg_parser()
    db, cur = conn_DB(ini_file, db_name)
    
    if tid == '1' or tid == '2':
        portion = 0.2
    elif tid == '3':
        portion = 0.1
    period = 140
    summary_update(db,cur,tid,period,portion)


if __name__ == '__main__':
    main()
