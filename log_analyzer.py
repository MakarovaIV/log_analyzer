#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import configparser
import gzip
import json
import os
import re
import statistics
import logging
import sys
from datetime import datetime
from string import Template

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip
#                      [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for"
#                     "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "REPORT_SIZE": 10,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./test_data/find_gz",
    "LOG_FILE": "./monitoring.log",
    "MAX_ERROR_PERC": 10,  # in %
}

DEFAULT_CONFIG_PATH = './test_config.ini'

# nginx-access-ui.log-20170630.gz
FILE_PATTERN = r'^nginx-access-ui\.log-(\d{8})(\.gz)?$'

# 1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300]
# "GET /api/v2/banner/25019354 HTTP/1.1" 200 927
# "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5"
# "-" "1498697422-2190034393-4708-9752759" "dc7161be3" 0.390
ROW_PATTERN = r'^(.+) (.+) (.+) \[(.+)\] \"(?P<request>.+)\" 200 ' \
              r'(.+) \"(.+)\" \"(.+)\" \"(.+)\" \"(.+)\" \"(.+)\" ' \
              r'(?P<request_time>.+)$'

# GET /api/v2/banner/25019354 HTTP/1.1
URL_PATTERN = r'^(?P<method>.+) (?P<url>.+) (?P<protocol>.+)$'

TEMPLATE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "report.html")
)


def get_config():
    try:
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('--config', help='Config file path')
        args = arg_parser.parse_args()

        config_file_path = args.config if args.config else DEFAULT_CONFIG_PATH
        cfg_parser = configparser.ConfigParser()
        cfg_parser.optionxform = str
        cfg_parser.read_file(open(config_file_path, "r"))

        return dict(cfg_parser.items("DEFAULT"))

    except Exception:
        logging.exception('Error in trying get config')


def merge_configs(default_config, config_from_file):
    try:
        if not config_from_file:
            return default_config

        cfg = {}
        for param in default_config:
            cfg[param] = config_from_file[param] \
                if (param in config_from_file) \
                else default_config[param]
        return cfg

    except Exception:
        logging.exception('Error in trying merge default and external configs')


def logging_set_up(log_file_name):
    if log_file_name is None or "":
        log_name = None
    else:
        log_name = log_file_name

    logging.basicConfig(filename=log_name,
                        filemode="w",
                        format='[%(asctime)s] %(levelname)s %(message)s',
                        datefmt='%Y.%m.%d%H:%M:%S',
                        level=logging.INFO)


def find_latest_file(file_pattern, file_path):
    try:
        latest_file_name, latest_create_time, \
            path, file_extension = None, None, None, None
        regex = re.compile(file_pattern)

        aaa = file_path if os.path.isabs(file_path) \
            else os.path.abspath(file_path)

        for path, dirs, files in os.walk(aaa):
            filtered_files = filter(lambda file: regex.match(file), files)
            for name in filtered_files:
                file_time = regex.match(name).group(1)

                if not latest_create_time or file_time > latest_create_time:
                    latest_create_time = file_time
                    latest_file_name = name
                    file_extension = regex.match(name).group(2)

        logging.info("The latest log file is %s/%s",
                     path,
                     latest_file_name)
        return {"name": latest_file_name,
                "time": latest_create_time,
                "path": path,
                "extension": file_extension}

    except Exception:
        logging.exception('Error in trying find latest log file')


def open_file(name, path, extension):
    file = None
    if name:
        full_name = path + '/' + name
        logging.info("File %s is opening", name)

        try:
            if extension == ".gz":
                file = gzip.open(filename=full_name, mode="rt")
            else:
                file = open(full_name)

        except Exception:
            logging.exception('Cannot open file')

    return file


def read_lines_from_file(sources):
    for row in sources:
        yield row
    sources.close()


def parse_logs(lines, max_error_perc):
    regex_row = re.compile(ROW_PATTERN)
    regex_url = re.compile(URL_PATTERN)

    total_count = 0
    error_count = 0
    for line in lines:
        matches = None
        total_count += 1

        try:
            matches = regex_row.match(line)
        except Exception:
            logging.exception('Cannot parse "%s"', line)

        if matches:
            request = matches.groupdict()['request']
            request_time = matches.groupdict()['request_time']

            try:
                url_string = regex_url.match(request).groupdict()['url']
            except Exception:
                logging.exception('Cannot parse url in request "%s"', request)

            yield {"url": url_string, "request_time": request_time}
        else:
            error_count += 1
            error_perc = (error_count / total_count) * 100

            if error_perc >= max_error_perc:
                logging.error(f'Error count > {max_error_perc}%')
                sys.exit(1)

            yield None


def collect_data_for_table(lines, report_size):
    if not lines:
        return []

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

    sorted_data = sorted(template_data,
                         key=lambda t: t["time_sum"],
                         reverse=True)
    logging.info("Data for report is analyzed")

    return sorted_data[:int(report_size)]


def render_html(data):
    try:
        with open(TEMPLATE_PATH, "rb") as f:
            template = Template(f.read().decode("utf-8"))

        return template.safe_substitute(
            {"table_json": json.dumps(data)}
        )
    except Exception:
        logging.exception("HTML rendering failed")


def save_to_file(content, name, path):
    path = os.path.abspath(path)
    if not os.path.exists(path):
        os.makedirs(path, mode=0o777)

    file_path = os.path.join(path, name)

    with open(file_path, "w") as f:
        f.write(content)
    logging.info("Report file is saved %s", file_path)


def get_file_name_from_meta(file_meta):
    date = datetime.strptime(file_meta["time"], '%Y%m%d')
    return "report-" + date.strftime('%Y.%m.%d') + ".html"


def check_file_report_exists(file_meta, path):
    file_name = get_file_name_from_meta(file_meta)
    file_path = os.path.abspath(
        os.path.join(path, file_name)
    )

    return os.path.exists(file_path)


def main(effective_config):
    file_meta = find_latest_file(FILE_PATTERN,
                                 effective_config["LOG_DIR"])
    if not file_meta["name"]:
        return

    if check_file_report_exists(file_meta,
                                effective_config["REPORT_DIR"]):
        logging.info("File report is existed %s", file_meta["name"])
        return

    logfile = open_file(name=file_meta["name"],
                        path=file_meta["path"],
                        extension=file_meta["extension"])
    if not logfile:
        return

    log_lines = read_lines_from_file(logfile)
    if not log_lines:
        return

    parsed_data = parse_logs(log_lines,
                             float(effective_config["MAX_ERROR_PERC"]))
    if not parsed_data:
        return

    data_for_table = collect_data_for_table(parsed_data,
                                            effective_config["REPORT_SIZE"])
    report_content = render_html(data_for_table)
    if not report_content:
        return

    save_to_file(report_content,
                 get_file_name_from_meta(file_meta),
                 effective_config["REPORT_DIR"])


if __name__ == "__main__":
    try:
        config_from_file = get_config()
        effective_config = merge_configs(config, config_from_file)
        logging_set_up(effective_config["LOG_FILE"])
        main(effective_config)

    except Exception:
        logging.exception("Unexpected error")
    except KeyboardInterrupt:
        logging.exception("Interrupted by user")
