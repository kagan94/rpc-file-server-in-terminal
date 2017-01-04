from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from SocketServer import ThreadingMixIn
from argparse import ArgumentParser
import os
import time

current_path = os.path.abspath(os.path.dirname(__file__))
TEMP_DIR = os.path.join(current_path, "files_on_server")


class FileService:
    def list_files(self, n):
        files = os.listdir(TEMP_DIR)
        return files

    def upload_file(self, file_name, file_content):
        error = ""
        file_path = os.path.join(TEMP_DIR, file_name)

        # Check file existence before uploading
        if os.path.isfile(file_path):
            error = "Requested file already exists in the temp folder."

        # Upload the file
        else:
            with open(file_path, "wb") as tf:
                tf.write(file_content)
        return error

    def download_file(self, file_name):
        error, file_content = "", ""
        file_path = os.path.join(TEMP_DIR, file_name)

        # Check file existence before downloading
        if os.path.isfile(file_path):
            with open(file_path, "r") as f:
                file_content = f.read()
        else:
            error = "File doesn't exist on server"

        return error, file_content

    def delete_file(self, file_name):
        error = ""
        file_path = os.path.join(TEMP_DIR, file_name)

        # Check file existence before deleting
        if os.path.isfile(file_path):
            os.remove(file_path)
            # 'Requested file was deleted successfully'
        else:
             error = "Requested file doesn't exist"
        return error

    def rename_file(self, current_file_name, new_file_name):
        error = ""
        file_path = os.path.join(TEMP_DIR, current_file_name)
        new_file_path = os.path.join(TEMP_DIR, new_file_name)

        # Check file existence before renaming
        if os.path.isfile(file_path):
            os.rename(file_path, new_file_path)
        else:
             error = "Requested file doesn't exist"

        return error

    def test_multithreading(self, number):
        while True:
            print number
            time.sleep(0.3)


# Restrict to a particular path.
class FServiceRequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


class AsyncXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass


if __name__ == '__main__':
    print "App started"

    DEFAULT_SERVER_PORT = 7777
    DEFAULT_SERVER_INET_ADDR = '127.0.0.1'

    parser = ArgumentParser()
    parser.add_argument('-H', '--host',
                        help='Server INET address '
                        'defaults to %s' % DEFAULT_SERVER_INET_ADDR,
                        default=DEFAULT_SERVER_INET_ADDR)
    parser.add_argument('-p', '--port', type=int,
                        help='Server TCP port, '
                        'defaults to %d' % DEFAULT_SERVER_PORT,
                        default=DEFAULT_SERVER_PORT)
    args = parser.parse_args()

    # Instance of file service
    file_service_inst = FileService()
    server_sock = (args.host, args.port)

    # Create XML_server
    server = AsyncXMLRPCServer(server_sock,
                               requestHandler=FServiceRequestHandler)
    server.register_introspection_functions()
    server.register_multicall_functions()

    # Register all functions of the FileService instance
    server.register_instance(file_service_inst)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print 'Ctrl+C issued, terminating ...'
    finally:
        server.shutdown()       # Stop the serve-forever loop
        server.server_close()   # Close the sockets
    print 'Terminating ...'
