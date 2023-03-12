import unittest
from log_analyzer import parse_logs

lines = ["1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] "
         "\"GET /api/v2/banner/25019354 HTTP/1.1\" 200 927 \"-\" "
         "\"Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5\" \"-\" "
         "\"1498697422-2190034393-4708-9752759\" \"dc7161be3\" 0.390"

         "1.196.145.32 -  - [29/Jun/2017:03:50:22 +0300] "
         "\"GET /api/v2/test/25019354 HTTP/1.1\" 200 927 \"-\" "
         "\"Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5\" \"-\" "
         "\"1498697422-2190034393-4708-9752759\" \"dc7161be3\" 0.123"

         "1.25.116.32 -  - [29/Jun/2017:03:50:22 +0300] "
         "\"GET /api/v2/banner/123321 HTTP/1.1\" 200 927 \"-\" "
         "\"Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5\" \"-\" "
         "\"1498697422-2190034393-4708-9752759\" \"dc7161be3\" 0.235"
         ]

positive_max_error_perc = 10

negative_max_error_perc = 1


class ParseDataTests(unittest.TestCase):
    def test_parse_logs(self):
        parsed_lines = parse_logs(lines, positive_max_error_perc)
        for line in parsed_lines:
            pass

        self.assertEqual({'request_time': '0.235', 'url': '/api/v2/banner/123321'}, line)

    def test_error_perc(self):
        parse_logs(lines, negative_max_error_perc)
        self.assertRaises(SystemExit)
