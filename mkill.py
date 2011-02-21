#!/usr/bin/python

import argparse
import getpass
import MySQLdb
import sys

parser = argparse.ArgumentParser(description="MySQL Kill thread wrapper tool.")

parser.add_argument("-u", type=str, required=True, metavar="USER", \
        dest="username", help="String. User name for log in.")

parser.add_argument("-p", type=str, metavar="PASSWORD", default=None, \
        dest="password", help="String. User password for log in.")

parser.add_argument("-hh", type=str, default="localhost", metavar="HOST", \
        dest="host", help="String. Host name (Defatult: 'localhost').")

parser.add_argument("--conn", action="store_const", const="CONNECTION", \
        default="QUERY", dest="modifier", help=("Boolean. Indicates kill " + \
            "the connection that handles the query (other queries handled " + \
                "by the same connection will die too)."))

parser.add_argument("--user", type=str, default=None, \
        help=("String. Marks for kill all threads matching indicated user " + \
                "as owner (default: none)."))

parser.add_argument("--database", type=str, default=None, \
        help=("String. Marks for kill all threads matching database where " + \
                "query is running (default: none)."))

parser.add_argument("--host", type=str, default=None, \
        help=("String. Marks for kill all threads matching indicated user " + \
                "as owner (default: none)."))

parser.add_argument("--no-schema", action="store_true", default=False, \
        dest="noschema", help=("String. Marks for kill all threads running " + \
            "over none schema."))

parser.add_argument("-t", type=int, nargs="*", default=None, metavar="ID", \
        dest="threadids", help="Integer. Specific thread IDs to kill.")

def main(args):
    try:
        conn = MySQLdb.connect(user=args.username, passwd=args.password, host=args.host)
    except MySQLdb.OperationalError, (errno, desc):
        print """Error %d connecting to host: "%s".""" % (errno, desc)
        return 1

    c = conn.cursor()
    query = "KILL %s %%d" % args.modifier
    count = 0
    if args.threadids:
        for id in args.threadids:
            try:
                c.execute(query % id)
                count += 1
            except MySQLdb.OperationalError, (errno, desc):
                print """Error %d for thread id %d: "%s".""" % (errno, id, desc)
    else:
        c.execute("SHOW PROCESSLIST")
        rows = c.fetchall()
        for row in rows:
            (id, user, host, db, command, time, state, info) = row
            filters = []
            if args.user:     filters.append(args.user == user)
            if args.database: filters.append(args.database == db)
            if args.host and host:  
                filters.append(args.host == host.split(":")[0])
            if args.noschema: filters.append(args.host is None)
            if len(filters) and all(filters): 
                c.execute(query % id)
                count += 1
    c.close()
    conn.close()
    print "%d threads killed." % count
    return 0
        
if __name__ == '__main__':
    args = parser.parse_args()
    if not args.password: args.password = getpass.getpass()
    sys.exit(main(args))