import unittest
from log_analyzer import find_latest_file


file_pattern = r'^nginx-access-ui\.log-(\d{8})(\.gz)?$'

gz_file_path = "../test_data/find_gz"

plain_file_path = "../test_data/find_plain"

unsupported_file_path = "../test_data/unsupported_extensions"


class FindLatestFileTests(unittest.TestCase):
    def test_find_latest_gz_file(self):
        latest_file = find_latest_file(file_pattern, gz_file_path)
        self.assertEqual("nginx-access-ui.log-20230310.gz", latest_file["name"])

    def test_find_latest_plain_file(self):
        latest_file = find_latest_file(file_pattern, plain_file_path)
        self.assertEqual("nginx-access-ui.log-20230310", latest_file["name"])

    def test_find_unsupported_extension(self):
        latest_file = find_latest_file(file_pattern, unsupported_file_path)
        self.assertEqual(None, latest_file["name"])
