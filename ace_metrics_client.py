# -*- coding: utf-8 -*-
"""Python client for collecting IBM Integration Bus metrics and exporting to Prometheus pushgateway."""
import sys
import os
import time
import traceback
import platform
import requests
import argparse
from requests import ConnectionError
from urllib3.exceptions import ResponseError
from modules.ace_brokers import (
    get_brokers_status,
    format_broker,
    get_broker_items)
from modules.ace_exec_groups import format_exec_groups
from modules.ace_applications import format_applications
from modules.ace_message_flows import format_message_flows
from log.logger_client import set_logger
from modules.ace_api import (
    run_ace_command,
    get_platform_params_for_commands)


logger = set_logger()


class PrometheusBadResponse(Exception):
    pass


def static_content():
    """Client name and version."""
    name = "ace-metrics-pyclient"
    version = "1.0.0"
    return '{0} v.{1}'.format(name, version)


def get_version_from_env():
    """Get Integration Bus version from env variable."""
    ace_version = os.getenv("MQSI_VERSION_V")
    if ace_version:
        logger.info("Integration Bus version is defined via MQSI_VERSION_V environment variable.")
    else:
        logger.info("Integration Bus default version is used.")
        ace_version = "12"
    return ace_version


def parse_commandline_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(prog='ace_metrics_client.py')
    parser.add_argument('--pghost', metavar='pushgatewayHost', nargs='?', default=platform.node(), dest='pushgateway_host', help='pushgateway host')
    parser.add_argument('--pgport', metavar='pushgatewayPort', nargs='?', default='9091', dest='pushgateway_port', help='pushgateway port')
    parser.add_argument('--acever', metavar='aceversion', nargs='?', default=None, dest='ace_cmd_ver', help='ACE version: 11 or 12')
    parser.add_argument('--collectint', metavar='collectInterval', nargs='?', default=60, type=int, dest='sleep_interval', help='time interval between collecting metrics')
    args = parser.parse_args()
    if (args.ace_cmd_ver is None) or ((args.ace_cmd_ver != '11') and (args.ace_cmd_ver != '12')):
        logger.info("Trying to determine Integration Bus version from environment variable MQSI_VERSION_V.")
        ace_cmd_ver = get_version_from_env()
    else:
        ace_cmd_ver = args.ace_cmd_ver
    return args.pushgateway_host, args.pushgateway_port, ace_cmd_ver, abs(args.sleep_interval)


def put_metric_to_gateway(metric_data, job, pushgateway_host, pushgateway_port):
    """Sends data to Prometheus pushgateway."""
    src_url = "http://{0}:{1}".format(pushgateway_host, pushgateway_port)
    headers = {"Content-Type": "text/plain; version=1.0.0"}
    dest_url = "{0}/metrics/job/{1}".format(src_url, job)
    logger.info("Destination url: {0}".format(dest_url))
    # Debug info
    # logger.info("Metric data to push: {0}".format(metric_data))
    try:
        response = requests.put(dest_url, data=metric_data, headers=headers)
        if not response.ok:
            raise PrometheusBadResponse("Bad response - {0} from {1}\nResponseText: {2}".format(response, dest_url, response.text))
        logger.info("Success! Server response: {0}".format(response))
    except (ConnectionError, ResponseError):
        raise PrometheusBadResponse("{0} is not available!".format(dest_url))


def get_ace_metrics(pushgateway_host, pushgateway_port, mqsilist_command, bip_codes_brokers, bip_codes_components):
    start_time = time.time()
    logger.info("Starting metrics collecting for Integration Bus!")
    try:
        brokers_data = run_ace_command(task=mqsilist_command)
        brokers = get_brokers_status(brokers_data=brokers_data, bip_codes=bip_codes_brokers)
        for broker in brokers:
            broker_name, status, qm_name = broker
            broker_data = format_broker(
                broker_name=broker_name,
                status=status,
                qm_name=qm_name)
            if status == 'running':
                broker_row_data = run_ace_command(
                    task='get_broker_objects',
                    broker_name=broker_name)
                exec_groups, applications, message_flows = get_broker_items(
                    broker_row_data=broker_row_data,
                    bip_codes=bip_codes_components)
                exec_groups_data = format_exec_groups(
                    exec_groups=exec_groups,
                    bip_codes=bip_codes_components)
                applications_data = format_applications(
                    applications=applications,
                    broker_name=broker_name,
                    bip_codes=bip_codes_components)
                message_flows_data = format_message_flows(
                    message_flows=message_flows,
                    broker_name=broker_name,
                    bip_codes=bip_codes_components)
                metric_data = "{0}{1}{2}{3}".format(
                    broker_data,
                    exec_groups_data,
                    applications_data,
                    message_flows_data)
                put_metric_to_gateway(
                    metric_data=metric_data,
                    job=broker_name,
                    pushgateway_host=pushgateway_host,
                    pushgateway_port=pushgateway_port)
                logger.info("All metrics pushed successfully!")
            else:
                put_metric_to_gateway(
                    metric_data=broker_data,
                    job=broker_name,
                    pushgateway_host=pushgateway_host,
                    pushgateway_port=pushgateway_port)
                logger.warning("The status of broker is {0}\nOther metrics will not be collected!".format(status))
        logger.info("Script finished in - {0} seconds -".format(time.time() - start_time))
    except PrometheusBadResponse as error:
        logger.error(error)
    except Exception as e:
        tb = sys.exc_info()[-1]
        stk = traceback.extract_tb(tb, 1)[0]
        logger.error("Function: {0}\n{1}".format(stk, e))


if __name__ == "__main__":
    logger.info("Run {0}".format(static_content()))
    pushgateway_host, pushgateway_port, ace_ver, sleep_interval = parse_commandline_args()
    logger.info("Integration Bus version: {0}".format(ace_ver))
    logger.info("Metrics will be collected every {0} seconds".format(sleep_interval))
    mqsilist_command, bip_codes_brokers, bip_codes_components = get_platform_params_for_commands(ace_ver=ace_ver)
    while True:
        get_ace_metrics(
            pushgateway_host=pushgateway_host,
            pushgateway_port=pushgateway_port,
            mqsilist_command=mqsilist_command,
            bip_codes_brokers=bip_codes_brokers,
            bip_codes_components=bip_codes_components)
        time.sleep(sleep_interval)
