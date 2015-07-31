import ConfigParser
import MySQLdb as mdb

def conn_DB(ini_file, db_name):
    config = ConfigParser.ConfigParser()
    config.read(ini_file)
    info = {}
    values = config.options(db_name)
    for value in values:
        try:
            info[value] = config.get(db_name, value)
        except:
            print("Error parsing config file!")

    db = mdb.connect(host=info['host'],user=info['user'],
            passwd=info['passwd'],db=info['db'])
    cur = db.cursor()
    db.set_character_set('utf8')
    cur.execute('SET NAMES utf8;')
    cur.execute('SET CHARACTER SET utf8;')
    cur.execute('SET character_set_connection=utf8;')

    return (db, cur)
