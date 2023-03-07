#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gzip
import os
import re

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
}

FILE_PATH = r'/home/makarovaiv/Downloads/logs'

# nginx-access-ui.log-20170630.gz
FILE_PATTERN = r'^nginx-access-ui\.log-(\d{8})\.(gz|log)$'

# 1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/25019354 HTTP/1.1" 200 927 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752759" "dc7161be3" 0.390
ROW_PATTERN = r'^(.+) (.+) (.+) \[(.+)\] \"(?P<request>.+)\" 200 (.+) \"(.+)\" \"(.+)\" \"(.+)\" \"(.+)\" \"(.+)\" (?P<request_time>.+)$'

# GET /api/v2/banner/25019354 HTTP/1.1
URL_PATTERN = r'^(?P<method>.+) (?P<url>.+) (?P<protocol>.+)$'


def find_latest_file(file_pattern, file_path):
    latest_file, latest_create_time, path, file_extension = None, None, None, None
    regex = re.compile(file_pattern)
    for path, dirs, files in os.walk(file_path):
        filtered_files = filter(lambda file: regex.match(file), files)
        for name in filtered_files:
            file_time = regex.match(name).group(1)
            if not latest_create_time or file_time > latest_create_time:
                latest_create_time = file_time
                latest_file = name
                file_extension = regex.match(name).group(2)
    return {"name": latest_file, "time": latest_create_time, "path": path, "extension": file_extension}


def open_file(name, path, extension):
    if name:
        full_name = path + '/' + name
        if extension.endswith("gz"):
            return gzip.open(filename=full_name, encoding='utf-8')
        elif extension.endswith("log"):
            return open(full_name)


def read_lines_from_file(sources):
    for row in sources:
        yield row


def parse_logs(lines):
    regex_row = re.compile(ROW_PATTERN)
    regex_url = re.compile(URL_PATTERN)

    for line in lines:
        matches = regex_row.match(line)
        if matches:
            request = matches.groupdict()['request']
            request_time = matches.groupdict()['request_time']
            url_string = regex_url.match(request).groupdict()['url']
            yield {"url": url_string, "request_time": request_time}
        else:
            yield None


def main():
    result_table = {}
    file = find_latest_file(FILE_PATTERN, FILE_PATH)
    logfile = open_file(name=file["name"], path=file["path"], extension=file["extension"])
    log_lines = read_lines_from_file(logfile)
    parsed_data = parse_logs(log_lines)
    for data in parsed_data:
        if data:
            if data["url"] in result_table:
                current_record = result_table[data["url"]]
                result_table[data["url"]] = {"count": current_record["count"] + 1,
                                             "request_time": current_record["request_time"] + float(data["request_time"])}
            else:
                result_table[data["url"]] = {"count": 1, "request_time": float(data["request_time"])}
        else:
            pass
            # print("-------------------")

    print("result:", result_table)


if __name__ == "__main__":
    main()
