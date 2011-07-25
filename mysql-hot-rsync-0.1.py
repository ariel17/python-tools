#!/usr/bin/python2.4

## mysql-hot-rsync : v0.1
##
## http://devsec.org/software/mysql-hot-rsync/
##
## Thor Kooda
## 2006-04-19

## USAGE:  mysql-hot-rsync <dest dir> [db [table ...] ]

## ABOUT:
##  - uses rsync to save a safe backup of live mysql databases and/or tables

## NOTES:
##  - if no db is passed, it will save all databases
##  - if no tables are passed, it will save all tables

## ALGORITHM:
##  - compiles a dict of dbs and their tables to be processed:
##    {'db1': ['table1', 'table2', 'table3'],
##     'db2': ['tableA', 'tableB', 'tableC']}
##  - processes the dict of dbs/tables

import sys
import os
import MySQLdb
import re
import subprocess

# defaults
mysql_user = "root"
mysql_pass = "XXXXXXXXXX"
rsync_cmd  = "/usr/bin/rsync"
rsync_args = "--quiet --perms --links --times --numeric-ids"

# mysql connect function
def do_connect():
    try:
        con = MySQLdb.Connect( user = mysql_user,
                               passwd = mysql_pass )
    except:
        print >>sys.stderr, "error: mysql connect"
        sys.exit( 1 )
    return con

# mysql query function    
def do_query( cur, query ):
    try:
        cur.execute( query )
    except:
        print >>sys.stderr, "error: mysql query: '%s'" % query
        sys.exit( 1 )

# function to obtain datadir
def get_datadir():
    cur = con.cursor()
    do_query( cur, "SHOW VARIABLES LIKE 'datadir'" )
    var_datadir = cur.fetchone()[1]
    cur.close()
    return var_datadir

# build dict of db(s) and table(s) with db names as the keys and table lists
def get_tree():
    tree = dict()
    
    # if we've got the dbs and some tables..
    if len(sys.argv) >= 4:
        tree[ sys.argv[ 2 ] ] = sys.argv[ 3 : ] # store db and table(s)
        return tree
    
    # if we've got just the db..
    if len(sys.argv) >= 3:
        tree[ sys.argv[ 2 ] ] = [] # store only db
    else:
        # no dbs yet, find+store all dbs
        cur = con.cursor()
        do_query( cur, "SHOW DATABASES" )
        for db in cur.fetchall():
            tree[ db[0] ] = []
        cur.close()
    
    # store list of tables for each db
    for db in tree.keys():
        cur = con.cursor()
        do_query( cur, "SHOW TABLES FROM %s" % db )
        for table in cur.fetchall():
            tree[ db ].append( table[0] )
        cur.close()
    
    return tree

# function to backup single table
def do_backup_table( db, table ):
    path_db_dir = os.path.join(var_datadir, db)
    
    if not os.access( path_db_dir, os.R_OK ):
        print >>sys.stderr, "warning: skipping unreadable database dir: '%s'" % path_db_dir
        return False
    
    # build list of file names to backup (this could probably be done by a rsync pattern)
    regex = "^%s\.*" % table
    pattern = re.compile( regex )
    src_files = []
    for root, dirs, files in os.walk( path_db_dir ):
        for file in files:
            if pattern.match( file ):
                file_path = "%s/%s/%s" % ( var_datadir, db, file )
                if not os.access( file_path, os.R_OK ):
                    print >>sys.stderr, "warning: skipping unreadable file: '%s'" % file_path
                    continue
                src_files.append( file )
    
    return do_backup_table_files( db, table, src_files )

# flush+lock+flush table..
def do_table_lock( cur, db, table ):
    do_query( cur, "USE %s" % db )
    do_query( cur, "FLUSH TABLE %s" % table ) # flush one table
    do_query( cur, "LOCK TABLE %s WRITE" % table ) # lock one table
    do_query( cur, "FLUSH TABLE %s" % table ) # flush one table

# unlock table..
def do_table_unlock( cur ):
    do_query( cur, "UNLOCK TABLES" ) # unlock all tables

# function to backup all files for one table
def do_backup_table_files( db, table, src_files ):
    cur = con.cursor()
    do_table_lock( cur, db, table )
    
    for file in src_files:
        ## tkooda : 2006-04-19 : XXX FIXME: sanitize (strip "..", "/", and quotes from) db/table names
        cmd = "%s %s '%s/%s/%s' '%s/%s/'" % ( rsync_cmd, rsync_args, var_datadir, db, file, dest_dir, db)
        try:
            retcode = subprocess.call(cmd, shell=True)
            if retcode < 0:
                print >>sys.stderr, "error: child was terminated by signal", -retcode
            elif retcode > 0:
                print >>sys.stderr, "warning: rsync comand returned: '%s' ('%s')" % ( retcode, cmd )
        except OSError, e:
            print >>sys.stderr, "error: execution failed:", e
    
    do_table_unlock( cur )
    cur.close()
    return True


if __name__ == '__main__':

    # check argv
    if len(sys.argv) < 2:
        print >>sys.stderr, "usage: %s <dest dir> [db [table ... ] ]" % sys.argv[ 0 ]
        sys.exit( 2 )
    
    # check destination dir
    dest_dir = sys.argv[ 1 ]
    if not os.access( dest_dir, os.W_OK ):
        print >>sys.stderr, "error: nonwritable destination dir: '%s'" % dest_dir
        sys.exit( 1 )
    
    # mysql connect
    con = do_connect()
    
    # get mysql datadir
    var_datadir = get_datadir()
    
    # get dict of dbs/tables
    tree = get_tree()
    
    #print >>sys.stderr, tree # DEBUG
    
    for db in tree.keys():
        if not os.access( os.path.join(var_datadir, db), os.R_OK ):
            print >>sys.stderr, "warning: skipping invalid database: '%s'" % db
            continue
        if not tree[ db ]:
            print >>sys.stderr, "warning: skipping database with no tables: '%s'" % db
            continue
        for table in tree[ db ]:
            if do_backup_table( db, table ):
                print >>sys.stderr, "sync: %s.%s" % ( db, table )
