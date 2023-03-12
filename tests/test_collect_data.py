import unittest
from log_analyzer import collect_data_for_table, parse_logs

lines = ["1.25.116.32 -  - [29/Jun/2017:03:50:22 +0300] "
         "\"GET /api/v2/banner/123321 HTTP/1.1\" 200 927 \"-\" "
         "\"Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5\" \"-\" "
         "\"1498697422-2190034393-4708-9752759\" \"dc7161be3\" 0.235"
         ]

report_size = 10

positive_max_error_perc = 10


class CollectDataTests(unittest.TestCase):
    def test_collect_data_from_table(self):
        parsed_lines = parse_logs(lines, positive_max_error_perc)
        collected_data = collect_data_for_table(parsed_lines, report_size)
        self.assertEqual([{'count': 1,
                          'count_perc': 1.0,
                          'time_avg': 0.235,
                          'time_max': 0.235,
                          'time_med': 0.235,
                          'time_perc': 1.0,
                          'time_sum': 0.235,
                          'url': '/api/v2/banner/123321'}], collected_data)
