'''
This file get eid from db,
 and add 'eid' field to each json object of each comment

Usage: python geteid.py database user password source startdate enddate
       source could be: imdb, MF
       date in the format like: '2015-01-01'

Note: Make sure you have already get sentiment score before running this script

Author: Wenjun Wang
Date: May 29, 2015
'''
import MySQLdb as mdb
import sys
import json
import codecs
from dateutil.rrule import rrule,DAILY
from datetime import datetime

def walk_through(directory,cur,start,end):
	for dt in rrule(DAILY,dtstart = start, until = end):
		thisdate = dt.strftime('%Y-%m-%d')
		name = '%s_comments_%s.json' % (directory,thisdate)
		print name
		try:
			json_file = codecs.open(name,encoding='utf-8')
			comments = json.load(json_file)
			to_write = codecs.open(name,'w',encoding='utf-8')
			for i in xrange(0,len(comments)):
				entity = comments[i]
				#print str(len(entity))
				for j in xrange(0,len(entity)):
					comment = entity[j]
					#print str(len(comment))
					source = comment['source']
					#print source
					identity = comment['id']
					query = 'SELECT eid FROM entity WHERE \
					source = "' + source + '" AND id = "' + identity + '";'
					#print query
					cur.execute(query)
					row = cur.fetchall()
					comment['eid'] = row[0][0]
			json.dump(comments,to_write)	
		except Exception as exc:
			print "exception in file: %s" % name
			raise

def main():
	if len(sys.argv) < 4:
		print "Usage: python geteid.py db usr pwd source startdate enddate"
		print "source may be: imdb, MF"
		print "Date in the format like: 2015-01-01"
		sys.exit(1)

	database = sys.argv[1]
	usr = sys.argv[2]
	pwd = sys.argv[3]
	source = sys.argv[4]
	directory = "/home/mingf/comment_full/" + source
	start = datetime.strptime(sys.argv[5],'%Y-%m-%d').date()
	end = datetime.strptime(sys.argv[6],'%Y-%m-%d').date()
	#print directory

	db = mdb.connect(host="localhost",user=usr,passwd=pwd,db=database)
	cur = db.cursor()
	
	walk_through(directory,cur,start,end)

	cur.close()			
	db.close()

if __name__ == '__main__':
	main()
