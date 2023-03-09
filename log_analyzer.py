#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gzip
import json
import os
import re
import statistics
import sys
from datetime import datetime
from string import Template

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
FILE_PATTERN = r'^nginx-access-ui\.log-(\d{8})(\.gz)?'

# 1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/25019354 HTTP/1.1" 200 927 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752759" "dc7161be3" 0.390
ROW_PATTERN = r'^(.+) (.+) (.+) \[(.+)\] \"(?P<request>.+)\" 200 (.+) \"(.+)\" \"(.+)\" \"(.+)\" \"(.+)\" \"(.+)\" (?P<request_time>.+)$'

# GET /api/v2/banner/25019354 HTTP/1.1
URL_PATTERN = r'^(?P<method>.+) (?P<url>.+) (?P<protocol>.+)$'

TEMPLATE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "report.html")
)


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
        if extension == "gz":
            return gzip.open(filename=full_name, encoding='utf-8')
        else:
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


def collect_data_for_table(lines):
    result_table = {}
    total_request_count = 0
    total_request_time = 0
    for line in lines:
        if line:
            url = line["url"]
            request_time = float(line["request_time"])
            total_request_count += 1
            total_request_time += request_time

            if url in result_table:
                result_table[url].append(request_time)
            else:
                result_table[url] = [request_time]
        else:
            pass
            # print("-------------------")

    template_data = []
    for url in result_table:
        request_time_array = result_table[url]
        count = len(request_time_array)
        time_sum = sum(request_time_array)
        template_data.append({"url": url,
                              "count": count,
                              "count_perc": count / total_request_count,
                              "time_sum": time_sum,
                              "time_perc": time_sum / total_request_time,
                              "time_avg": time_sum / count,
                              "time_max": max(request_time_array),
                              "time_med": statistics.median(request_time_array)
                              })

    return template_data


def render_html(data):
    with open(TEMPLATE_PATH, "rb") as f:
        template = Template(f.read().decode("utf-8"))

    return template.safe_substitute(
        {"table_json": json.dumps(data)}
    )


def save_to_file(content, name):
    path = os.path.abspath(config["REPORT_DIR"])
    if not os.path.exists(path):
        os.makedirs(path, mode=0o777)

    file_path = os.path.join(path, name)

    f = open(file_path, "w")
    f.write(content)
    f.close()


def get_file_name_from_meta(file_meta):
    date = datetime.strptime(file_meta["time"], '%Y%m%d')
    return "report-" + date.strftime('%Y.%m.%d') + ".html"


def check_file_report_exists(file_report_name):
    file_name = get_file_name_from_meta(file_report_name)
    file_path = os.path.abspath(
        os.path.join(config["REPORT_DIR"], file_name)
    )

    return os.path.exists(file_path)


def main():
    file_meta = find_latest_file(FILE_PATTERN, FILE_PATH)
    if not check_file_report_exists(file_meta):
        logfile = open_file(name=file_meta["name"], path=file_meta["path"], extension=file_meta["extension"])
        if not logfile:
            return

        log_lines = read_lines_from_file(logfile)
        if not log_lines:
            return

        parsed_data = parse_logs(log_lines)
        data_for_table = collect_data_for_table(parsed_data)
        report_content = render_html(data_for_table)
        if not report_content:
            return

        save_to_file(report_content, get_file_name_from_meta(file_meta))


if __name__ == "__main__":
    main()
