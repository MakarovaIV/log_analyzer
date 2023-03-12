import unittest
from test_merge_configs import MergeConfigsTest
from test_find_latest_file import FindLatestFileTests


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(MergeConfigsTest)
    runner.run(FindLatestFileTests)


class ParseDataTests(unittest.TestCase):
    def test_parse_logs(self):
        pass


class CollectDataTests(unittest.TestCase):
    def test_collect_data_from_table(self):
        pass


class GenerateReportTest(unittest.TestCase):
    def test_generate_html_report(self):
        pass
