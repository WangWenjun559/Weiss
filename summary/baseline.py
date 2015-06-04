'''
This file implement two baseline methods to generate sentence: 
random and leadbased

The general idea is to first select the most positive/negative comments based on sentiment scores. Then use baseline methods to generate sentence list, which is composed of 10% of original comment sentences. Finally, we insert summary, corresponding cid, mid into database table 'summary'.

NOTE: 
1) We don't normalize the sentiment score here since long comment may be good comment;
2) By default, Random (mid = 1), LeadBased (mid = 2)

Usage: python baseline.py db usr pwd source
       source may be: imdb, MF, etc

Author: Wenjun Wang
Date: June 3rd, 2015

TODO: Consider exceptions, may need rollback
'''
import MySQLdb as mdb
import random
import sys
import math
import nltk

#Select 10% of sentences into the summary
PERCENT = 0.1
'''
walk_through - go through top 50 entities from a specific source
'''
def walk_through(db,cur,source):
	sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
	geteids = 'SELECT eid FROM entity WHERE source = "' + source \
	+ '" LIMIT 50;'
	cur.execute(geteids)
	rows = cur.fetchall()
	for row in rows:
		eid = row[0]
		target = []
		target.append(\
		#Get the most positive comment
		'SELECT cid,body from comment, \
		(select max(sentiment) as score from comment where eid = ' \
		+ str(eid) + ' and sentiment > 0) as temp \
		where comment.sentiment = temp.score and \
		comment.eid = ' + str(eid) \
		)
		target.append(\
		#Get the most negative comment
		'SELECT cid,body from comment, \
                (select min(sentiment) as score from comment where eid = ' \
                + str(eid) + ' and sentiment < 0) as temp \
                where comment.sentiment = temp.score and \
                comment.eid = ' + str(eid) \
		)
		for query in target:
			cur.execute(query)
			onerow = cur.fetchone()
			if onerow != None:
				#There exist corresponding comments
				cid = onerow[0]
				comment = onerow[1]
				sentence_list = sent_tokenizer.tokenize(comment)
				#Select some portion of sentences into the summary
				num = int(math.ceil(PERCENT*len(sentence_list)))
				#Random
				randomstr = random_comment(sentence_list,num)
				
				insert = 'INSERT INTO summary(cid,mid,score,body) VALUES\
				('+ str(cid) +',1,-1,"' + randomstr + '")'
				#print insert
				cur.execute(insert)
				'''
				cur.commit()
				'''
				#LeadBased
				leadstr = lead_comment(sentence_list,num)
				insert = 'INSERT INTO summary(cid,mid,score,body) VALUES\
				('+ str(cid) +',2,-1,"' + leadstr + '")'
				cur.execute(insert)
				db.commit() 

'''
random_comment - pick a list of random sentences from the sentence list of 
		the original comment, and convert the list to string
'''
def random_comment(sentence_list,num):
	idxlst = random.sample(xrange(0,len(sentence_list)),num)
	idxlst.sort()
	print idxlst
	randomstr = ''
	for idx in idxlst:
		randomstr += sentence_list[idx] + '\n'
	return randomstr

'''
lead_comment - pick a list of first sentences from the sentence list of 
	the original comment, and convert the list to string
'''
def lead_comment(sentence_list,num):
	leadstr = ''
	for idx in xrange(0,num):
		leadstr += sentence_list[idx] + '\n'
	return leadstr

def main():
	if len(sys.argv) < 3:
		print "Usage: python baseline.py db usr pwd source"
		sys.exit(1)
	database = sys.argv[1]
	usr = sys.argv[2]
	pwd = sys.argv[3]
	source = sys.argv[4]

	db = mdb.connect(host="localhost",user=usr,passwd=pwd,db=database)
	cur = db.cursor()

	walk_through(db,cur,source)

	cur.close()
	db.close()

if __name__ == '__main__':
	main()
