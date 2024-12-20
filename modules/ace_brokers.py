# -*- coding: utf-8 -*-
"""Various functions for ace brokers."""
from modules.ace_api import get_status


def get_metric_name(metric_label):
    """Returns pushgateway formatted metric name."""
    return 'ace_broker_{0}'.format(metric_label)


def get_metric_annotation():
    """Returns dictionary with annotations 'HELP' and 'TYPE' for metrics."""
    annotations = {
        'status': '# HELP {0} Current status of ACE broker.\n\
# TYPE {0} gauge\n'.format(get_metric_name('status'))}
    return annotations


def get_brokers_status(brokers_data, bip_codes):
    """Returns list with statuses for brokers."""
    output_list = brokers_data.split('\n')
    brokers = list()
    for record in filter(None, output_list):
        record_list = record.split()
        bip_code = record_list[0].replace(':', '')
        if bip_code in bip_codes.keys():
            qm_name = str()
            broker_name = record_list[bip_codes[bip_code][0]].replace("'", "")
            trim_last_dot = bip_codes[bip_code][3]
            if bip_codes[bip_code][1] is not None:
                qm_name = record_list[bip_codes[bip_code][1]].replace("'", "")
                if trim_last_dot == 'true':
                    qm_name = qm_name[:-1]
            status = record_list[bip_codes[bip_code][2]].replace("'", "").replace(".", "")
            brokers.append([broker_name, status, qm_name])
    return brokers


def get_broker_items(broker_row_data, bip_codes):
    """Returns lists with data for broker items: execution groups, applications, message flows."""
    output_list = broker_row_data.split('\n')
    exec_groups = list()
    applications = list()
    message_flows = list()
    for record in output_list:
        if record:
            bip_code = record.split()[0].replace(':', '')
            if bip_code in bip_codes.keys():
                if  bip_codes[bip_code][0] == 'exec_groups':
                    exec_groups.append(record)
                if  bip_codes[bip_code][0] == 'applications':
                    applications.append(record)
                if  bip_codes[bip_code][0] == 'message_flows':
                    message_flows.append(record)
    return exec_groups, applications, message_flows


def format_broker(broker_name, status, qm_name):
    """Returns string with all metrics for broker which ready to push to pushgateway."""
    metrics_annotation = get_metric_annotation()
    template_string = 'brokername="{0}", qmname="{1}"'.format(
        broker_name,
        qm_name)
    broker_metric = '{0}{{{1}}} {2}\n'.format(
        get_metric_name(metric_label='status'),
        template_string,
        get_status(status=status))
    broker_metric = '{0}{1}'.format(
        metrics_annotation['status'],
        broker_metric)
    return broker_metric
