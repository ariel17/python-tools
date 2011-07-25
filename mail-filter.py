#!/usr/local/bin/python
#
# This script is a helper to clean POP3 mailboxes
# containing malformed mails that hangs MUA's, that 
# are too large, or whatever...
#
# It iterates over the non-retrieved mails, prints
# selected elements from the headers and prompt the 
# user to delete bogus messages.
#
# Written by Xavier Defrang <xavier.defrang@brutele.be>
# 
# By Ariel17: 
# - parse parameters to get POP host and user, max lines to show for each mail.
# - forced to always ask for password.
# - Replaced "while 1" for boolean condition.
# - Replaced "bye" for boolean value.
# - Changed "for n in range()" for itering mails by id to a while condition 


import argparse
import getpass, poplib, re


parser = argparse.ArgumentParser(description="POP mail filter in Python :)")

parser.add_argument("-o", "--host", type=str, required=True, 
        help="POP mail hostname or IP address.")

parser.add_argument("-u", "--user", type=str, required=True, 
        help="POP mail user name.")

parser.add_argument("-m", "--maxlines", type=str, default=10, 
        help="Max number of lines to show for each mail. Default: 10.")

# Headers we're actually interrested in
rx_headers  = re.compile(r"^(From|To|Subject)")


if __name__ == '__main__':
    
    args = parser.parse_args()

    try:
    
        # Connect to the POPer and identify user
        pop = poplib.POP3(args.host)
        pop.user(args.user)
    
        POPPASS = getpass.getpass("Password for %s@%s:" % (args.user, args.host))
    
        # Authenticate user
        pop.pass_(POPPASS)
    
        # Get some general informations (msg_count, box_size)
        stat = pop.stat()
    
        # Print some useless information
        print "Logged in as %s@%s" % (args.user, args.host)
        print "Status: %d message(s), %d bytes" % stat
    
        bye = False # if must finish the cicle
        count_del = 0 # counting deleted mails
        msgnum = 1
        while msgnum <= stat[0] and not bye:
    
            # Retrieve headers
            response, lines, bytes = pop.top(msgnum, args.maxlines)
    
            # if True in ['EXTERNAL IP' in l for l in lines]:
            #     print "Message %d (%d bytes)" % (msgnum, bytes)
            #     print "-" * 30
            #     print "\n".join(filter(rx_headers.match, lines))
            #     print "-" * 30
            #                                                      
            #     pop.dele(msgnum)
            #     print "Message %d marked for deletion" % msgnum
            #     count_del += 1
    
            # Print message info and headers we're interrested in
            print "Message %d (%d bytes)" % (msgnum, bytes)
            print "-" * 30
            print "\n".join(filter(rx_headers.match, lines))
            print "-" * 30
    
            # Input loop
            must_continue = True
            while must_continue:
                k = raw_input("(d=delete, s=skip, v=view, q=quit) What?")
                if k in "dD":
                    # Mark message for deletion
                    k = raw_input("Delete message %d? (y/n)" % msgnum)
                    if k in "yY":
                        pop.dele(msgnum)
                        print "Message %d marked for deletion" % msgnum
                        count_del += 1
                    must_continue = False
                elif k in "sS":
                    print "Message %d left on server" % msgnum
                    must_continue = False
                elif k in "vV":
                    print "-" * 30
                    print "\n".join(lines)
                    print "-" * 30
                elif k in "qQ":
                    bye = True
                    must_continue = False
            msgnum += 1                    
    
        # Summary
        print "Deleting %d message(s) in mailbox %s@%s" % (count_del, args.user,
                args.host)
    
        # Commit operations and disconnect from server
        print "Closing POP3 session"
        pop.quit()
    
    except poplib.error_proto, detail:
    
        # Fancy error handling
        print "POP3 Protocol Error:", detail
