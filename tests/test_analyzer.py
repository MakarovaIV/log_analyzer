import unittest
from test_merge_configs import MergeConfigsTest
from test_find_latest_file import FindLatestFileTests
from test_parse_data import ParseDataTests
from test_collect_data import CollectDataTests
from test_generate_report import GenerateReportTest


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(MergeConfigsTest))
    test_suite.addTest(unittest.makeSuite(FindLatestFileTests))
    test_suite.addTest(unittest.makeSuite(ParseDataTests))
    test_suite.addTest(unittest.makeSuite(CollectDataTests))
    test_suite.addTest(unittest.makeSuite(GenerateReportTest))
    return test_suite


if __name__ == '__main__':
    mySuite = suite()
    runner = unittest.TextTestRunner()
    runner.run(mySuite)
