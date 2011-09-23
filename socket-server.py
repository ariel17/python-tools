#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: A simple socket server implementing reactor pattern. The message to
transmit follows this structure:

    [xxx] header: integer zero-filled to left. Indicates body's length.
    [xxx...] body: string, with length as the header value is.
"""
__author__ = "ariel17"

import socket
import select
import logging


FORMAT_LOG = '%(asctime)-15s %(levelname)s %(module)s PID#%(process)d '\
        '%(message)s'

logging.basicConfig(format=FORMAT_LOG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def recv(sock, length):
    """
    Implements an incremental message receiver.
    """
    msg = ''
    while len(msg) < length:
        chunk = sock.recv(length-len(msg))
        if chunk == '':
            raise RuntimeError("socket connection broken")
        msg = msg + chunk
    logger.debug("Raw message received: '%s' (%d)" % (msg, len(msg)))
    return msg


if __name__ == '__main__':
    logger.info(">>> Starting socket server")
    host = "0.0.0.0"
    port = 9000
    HEADER_LENGTH = 3

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(5)
    logger.debug("Now listening.")

    inputs = [sock, ]
    while 1:
        try:
            ready_in, ready_out, ready_err = select.select(inputs, [], [], 5)
        except select.error, e:
            logger.exception("There was an error executing 'select' "\
                    "statement:")
        except socket.error, e:
            logger.exception("There was an error with socket:")
                                                                           
        for r in ready_in:
            logger.debug("Socket has changes: %d" % r.fileno())
            if r == sock:
               # handle a new connection
                client, address = sock.accept()
                logger.info("Connection %d accepted from %s." %
                        (client.fileno(), address))
                inputs.append(client)
            else:
                # handle a request from an already connected client
                try:
                    body_length = recv(r, HEADER_LENGTH)
                except ValueError:
                    logger.exception("The value of body lengh received "\
                            "is not integer:")
                    continue
                logger.info("Header received: '%s'" % body_length)
                if len(body_length) == 0:
                    r.close()
                    inputs.remove(r)
                    logger.debug("Closed connection and removed client.")
                    continue
                message = recv(r, int(body_length))
                logger.info("Body received: '%s'" % message)
                response = "Done"
                message = "%s%s" % (str(len(response)).zfill(HEADER_LENGTH),
                        response)
                logger.debug("Sending response: %s" % message)
                r.send(message)
        
    # time to go: closing all input sockets still open
    logger.info("Closing connections")
    for i in inputs:
        i.close()

    logger.info(">>> Socket server is finished.")

