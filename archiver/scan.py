
# import logging
#
# from pyclamd import ClamdUnixSocket, ConnectionError
#
#
# logger = logging.getLogger(__name__)
#
#
# class CustomClamdUnixSocket(ClamdUnixSocket):
#
#     def custom_scan_file(self, file_path):
#         # Try and scan files. Catch exceptions if can't connect to socket
#         output = {
#             "found": None,
#             "error": None,
#             "version": self.version()
#         }
#
#         try:
#             scan_results = self.scan_file(file_path)
#         except ConnectionError:
#             scan_results = {file_path: ('ERROR', 'ConnectionError')}
#
#         if scan_results:
#             code, message = scan_results[file_path]
#             output[code.lower()] = message
#         return output
#
#
# clam_socket = CustomClamdUnixSocket()
