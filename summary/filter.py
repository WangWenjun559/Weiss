# -*- coding: utf8 -*-
import MySQLdb as mdb
#import nltk
import sys
import string
import re

REQUIRE = 10
#sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
table = string.maketrans("","")

def filtering(db,cur,source):
    geteids = 'SELECT eid FROM entity WHERE source = "' + source + '";'
    cur.execute(geteids)
    rows = cur.fetchall()
    count = 0

    print(len(rows))
    for row in rows:
        eid = row[0]
        getpos = 'SELECT body FROM comment WHERE sentiment > 0 and eid =' + str(eid)
        getneg = 'SELECT body FROM comment WHERE sentiment < 0 and eid =' + str(eid)
        cur.execute(getpos)
        rows_pos = cur.fetchall()
        cur.execute(getneg)
        rows_neg = cur.fetchall()
        # Need to check if it is necessary to pick a representative comment
        if len(rows_pos) < 5 or len(rows_neg) < 5:continue
        if len(rows_pos) > 30 or len(rows_neg) > 30:continue
        # Need to check if the comment need to be summarized
        # Threshold also for if we concatenate comments and treat it as one document
        num_sentences = 0
        num_word = 0
        for pos in rows_pos:
            body = unicode(pos[0],errors='ignore').encode('utf-8')
            if source == 'MetaFilter':
                body = re.sub('<[^<]+?>','',body)
            #num_sentences += len(sent_tokenizer.tokenize(body))
            body = body.translate(table,string.punctuation)
            num_word += len(body.split())
        #if num_sentences <= 2*len(rows_pos):continue
        if num_word < 500 or num_word > 2100:continue
        #num_sentences = 0
        num_word = 0
        for neg in rows_neg:
            body = unicode(neg[0],errors='ignore').encode('utf-8')
            if source == 'MetaFilter':
                body = re.sub('<[^<]+?>','',body)
            #num_sentences += len(sent_tokenizer.tokenize(body))
            body = body.translate(table,string.punctuation)
            num_word += len(body.split())
        #if num_sentences <= 2*len(rows_neg):continue
        if num_word < 500 or num_word > 2100:continue
        
        count += 1
        print(str(eid))
        insert = 'INSERT INTO mini_entity(eid) VALUES (' + str(eid) + ')'
        cur.execute(insert)
        db.commit()
        if count == REQUIRE:break
    #print(str(count))

def main():
    source = sys.argv[1]
    db = mdb.connect(host="localhost",user="weiss",passwd="washington",db="weiss");
    cur = db.cursor()
    db.set_character_set('utf8')
    cur.execute('SET NAMES utf8;')
    cur.execute('SET CHARACTER SET utf8;')
    cur.execute('SET character_set_connection=utf8;')

    filtering(db,cur,source)

    cur.close()
    db.close()

if __name__ == '__main__':
    main()
