import os
import unittest
import log_analyzer as lg_an

test_default_config = {
    "INT_PARAM": 10,
    "STR_PARAM": "str_default",
    "PARAM_ONLY_IN_DFAULT": 'test_default'
}

external_config = {
    "INT_PARAM": 20,
    "STR_PARAM": "str_ext",
    "EXCEED_PARAM": 100,
}

lines = ["1.25.116.32 -  - [29/Jun/2017:03:50:22 +0300] "
         "\"GET /api/v2/banner/123321 HTTP/1.1\" 200 927 \"-\" "
         "\"Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5\" \"-\" "
         "\"1498697422-2190034393-4708-9752759\" \"dc7161be3\" 0.235"
         ]

report_size = 10

positive_max_error_perc = 10

negative_max_error_perc = 1

file_pattern = r'^nginx-access-ui\.log-(\d{8})(\.gz)?$'

gz_file_path = "./test_data/find_gz"

plain_file_path = "./test_data/find_plain"

unsupported_file_path = "test_data/unsupported_extensions"

config = {
    "REPORT_SIZE": 10,
    "REPORT_DIR": "./test_reports",
    "LOG_DIR": "./test_data/find_plain",
    "LOG_FILE": "./monitoring.log",
    "MAX_ERROR_PERC": 10,
}

expected_report_path = "test_reports/report-2023.03.10.html"


class AnalyzerTests(unittest.TestCase):
    def test_merge_two_configs(self):
        merged_cfg = lg_an.merge_configs(test_default_config, external_config)
        self.assertEqual(external_config["INT_PARAM"], merged_cfg["INT_PARAM"])
        self.assertEqual(external_config["STR_PARAM"], merged_cfg["STR_PARAM"])
        self.assertEqual(test_default_config["PARAM_ONLY_IN_DFAULT"], merged_cfg["PARAM_ONLY_IN_DFAULT"])
        self.assertNotIn("EXCEED_PARAM", merged_cfg)

    def test_without_ext_config(self):
        merged_cfg = lg_an.merge_configs(test_default_config, None)
        self.assertEqual(test_default_config["INT_PARAM"], merged_cfg["INT_PARAM"])

    def test_without_default_config(self):
        lg_an.merge_configs(None, external_config)
        self.assertRaises(Exception)

    def test_collect_data_from_table(self):
        parsed_lines = lg_an.parse_logs(lines, positive_max_error_perc)
        collected_data = lg_an.collect_data_for_table(parsed_lines, report_size)
        self.assertEqual([{'count': 1,
                          'count_perc': 1.0,
                          'time_avg': 0.235,
                          'time_max': 0.235,
                          'time_med': 0.235,
                          'time_perc': 1.0,
                          'time_sum': 0.235,
                          'url': '/api/v2/banner/123321'}], collected_data)

    def test_parse_logs(self):
        parsed_lines = lg_an.parse_logs(lines, positive_max_error_perc)
        for line in parsed_lines:
            pass

        self.assertEqual({'request_time': '0.235', 'url': '/api/v2/banner/123321'}, line)

    def test_error_perc(self):
        lg_an.parse_logs(lines, negative_max_error_perc)
        self.assertRaises(SystemExit)

    def test_find_latest_gz_file(self):
        latest_file = lg_an.find_latest_file(file_pattern, gz_file_path)
        self.assertEqual("nginx-access-ui.log-20230310.gz", latest_file["name"])

    def test_find_latest_plain_file(self):
        latest_file = lg_an.find_latest_file(file_pattern, plain_file_path)
        self.assertEqual("nginx-access-ui.log-20230310", latest_file["name"])

    def test_find_unsupported_extension(self):
        latest_file = lg_an.find_latest_file(file_pattern, unsupported_file_path)
        self.assertEqual(None, latest_file["name"])

    def test_generate_html_report(self):
        file_meta = lg_an.find_latest_file(file_pattern, config["LOG_DIR"])
        logfile = lg_an.open_file(name=file_meta["name"], path=file_meta["path"], extension=file_meta["extension"])
        log_lines = lg_an.read_lines_from_file(logfile)
        parsed_data = lg_an.parse_logs(log_lines, float(config["MAX_ERROR_PERC"]))
        data_for_table = lg_an.collect_data_for_table(parsed_data, config["REPORT_SIZE"])
        report_content = lg_an.render_html(data_for_table)
        lg_an.save_to_file(report_content, lg_an.get_file_name_from_meta(file_meta), config["REPORT_DIR"])

        abs_report_path = os.path.abspath(expected_report_path)
        self.assertTrue(os.path.isfile(abs_report_path))


if __name__ == '__main__':
    unittest.main()
