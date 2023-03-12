import os.path
import unittest

import log_analyzer as lg_an

config = {
    "REPORT_SIZE": 10,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "../test_data/find_plain",
    "LOG_FILE": "./monitoring.log",
    "MAX_ERROR_PERC": 10,
}

expected_report_path = "./reports/report-2023.03.10.html"

file_pattern = r'^nginx-access-ui\.log-(\d{8})(\.gz)?$'


class GenerateReportTest(unittest.TestCase):
    def test_generate_html_report(self):
        file_meta = lg_an.find_latest_file(file_pattern, config["LOG_DIR"])
        logfile = lg_an.open_file(name=file_meta["name"], path=file_meta["path"], extension=file_meta["extension"])
        log_lines = lg_an.read_lines_from_file(logfile)
        parsed_data = lg_an.parse_logs(log_lines, float(config["MAX_ERROR_PERC"]))
        data_for_table = lg_an.collect_data_for_table(parsed_data, config["REPORT_SIZE"])
        report_content = lg_an.render_html(data_for_table)
        lg_an.save_to_file(report_content, lg_an.get_file_name_from_meta(file_meta), config["REPORT_DIR"])

        abs_report_path = os.path.abspath(expected_report_path)
        with open(abs_report_path) as f:
            report_file = f.read().rstrip()
        self.assertIn("<title>rbui log analysis report</title>", report_file)
