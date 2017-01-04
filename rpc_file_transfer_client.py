'''
Created on Oct 27, 2016

@author: devel
'''
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()

import os
import ntpath
from argparse import ArgumentParser
from sys import exit
from xmlrpclib import ServerProxy
from random import randint

# Constants -------------------------------------------------------------------
___NAME = 'MBoard Client'
___VER = '0.2.0.0'
___DESC = 'Simple Message Board Client (RPC version)'
___BUILT = '2016-10-27'
___VENDOR = 'Copyright (c) 2016 DSLab'

DEFAULT_SERVER_PORT = 7777
DEFAULT_SERVER_INET_ADDR = '127.0.0.1'


# Private methods -------------------------------------------------------------
def __info():
    return '%s version %s (%s) %s' % (___NAME, ___VER, ___BUILT, ___VENDOR)


# Not a real main method -------------------------------------------------------
def file_service_client_main(args):
    # Starting client
    LOG.info('%s version %s started ...' % (___NAME, ___VER))
    LOG.info('Using %s version %s' % (___NAME, ___VER))

    # RPC Server's socket address
    server_info = (args.host, int(args.port))
    try:
        server = ServerProxy("http://%s:%d" % server_info)

        LOG.info('Connected to "file service" XMLRPC server!')
        methods = filter(lambda x: 'system.' not in x, server.system.listMethods())
        LOG.debug('Remote methods are: [%s] ' % (', '.join(methods)))

    except KeyboardInterrupt:
        LOG.warn('Ctrl+C issued, terminating')
        exit(0)
    except Exception as e:
        LOG.error('Communication error %s ' % str(e))
        exit(1)

    try:
        # Process requested commands
        if args.list_files:
            print "Command list_files"

            files = server.list_files()

            if files:
                print "Files on server:"
                print ", ".join(files)
            else:
                print "No files on server"

        if args.upload_file:
            print "Command upload_file"

            file_path = args.upload_file
            file_name = ntpath.basename(file_path)

            # If file exists locally, then request command
            if os.path.isfile(file_path):
                # Read file locally
                with open(file_path, "r") as f:
                    file_content = f.read()

                # And send request to server to upload this file
                error = server.upload_file(file_name, file_content)
                print error if error else "File was uploaded successfully"
            else:
                print "Uploading file doesn't exist locally"

        if args.download_file:
            print "Command download_file"

            file_name = args.download_file
            error, file_content = server.download_file(file_name)

            if error:
                print error

            # If no errors, save file locally
            else:
                with open(file_name, "w") as f:
                    f.write(file_content)

                print "Requested file downloaded and saved successfully"

        if args.delete_file:
            print "Command delete_file"

            file_name = args.delete_file
            error = server.delete_file(file_name)

            print error if error else "Requested file was deleted successfully"

        if args.rename_file:
            names = args.rename_file

            if len(names) > 1:
                current_file_name, new_file_name = names
                error = server.rename_file(current_file_name, new_file_name)

                print error if error else "Requested file was renamed successfully"

            else:
                print "You didn't provide enough names to rename the file"
                print "(here should be 2 names: current_file_name new_file_name separated by space)"

            print "Command upload_file"

        if args.test_multithreading:
            '''
            Here we can just test multithreading for several clients
            by going into infinite loop (on server) and printing client's random number
            '''
            number = randint(0, 100)
            server.test_multithreading(number)

    except KeyboardInterrupt:
        print 'Ctrl+C issued, terminating ...'

    except Exception as e:
        print 'Error %s ' % str(e)

if __name__ == '__main__':
    parser = ArgumentParser(description=__info(),
                            version=___VER)
    parser.add_argument('-H', '--host',
                        help='Server INET address '
                        'defaults to %s' % DEFAULT_SERVER_INET_ADDR,
                        default=DEFAULT_SERVER_INET_ADDR)
    parser.add_argument('-p', '--port', type=int,
                        help='Server TCP port, '
                        'defaults to %d' % DEFAULT_SERVER_PORT,
                        default=DEFAULT_SERVER_PORT)

    ###################
    # Available actions
    # Command 'list_files' doesn't need any argument
    parser.add_argument('-lf', '--list_files', action='store_true',
                        help='List of files on server')
    parser.add_argument('-uf', '--upload_file', default='',
                        help='Upload file "file_path" to server')
    parser.add_argument('-df', '--download_file', default='',
                        help='Download file "file_name" from server')
    parser.add_argument('-delf', '--delete_file', default='',
                        help='Delete file "file_name" on server')
    parser.add_argument('-rf', '--rename_file', default=[], nargs='+',
                        help='Rename file "file_name" on server')

    # This method is to test server multithreading
    parser.add_argument('-tm', '--test_multithreading', action='store_true',
                        help='For testing multithreaded server (without arg)')
    args = parser.parse_args()

    file_service_client_main(args)

    print 'Terminating ...'
