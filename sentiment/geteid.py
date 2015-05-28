import MySQLdb as mdb
import sys
import glob
import json
import codecs

#cur = None
def walk_through(fpath,cur):
	files = glob.glob(fpath)
	for name in files:
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
		print "Usage: python geteid.py db usr pwd directory"
		sys.exit(1)

	database = sys.argv[1]
	usr = sys.argv[2]
	pwd = sys.argv[3]
	source = sys.argv[4]
	directory = "/home/mingf/comment_full/" + source + "_comments_*.json"
	print directory

	db = mdb.connect(host="localhost",user=usr,passwd=pwd,db=database)
	cur = db.cursor()
	
	walk_through(directory,cur)

	db.close()

if __name__ == '__main__':
	main()
