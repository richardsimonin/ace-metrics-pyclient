# -*- coding: utf-8 -*-
"""Various functions for ace message flows."""
from modules.ace_api import get_status


def get_metric_name(metric_label):
    """Returns pushgateway formatted metric name."""
    return 'ace_message_flow_{0}'.format(metric_label)


def get_metric_annotation():
    """Returns dictionary with annotations 'HELP' and 'TYPE' for metrics."""
    annotations = {
        'status': '# HELP {0} Current status of ACE message flow.\n\
# TYPE {0} gauge\n'.format(get_metric_name('status'))}
    return annotations


def format_message_flows(message_flows, broker_name, bip_codes):
    """Returns string with all metrics for all message flows which ready to push to pushgateway."""
    metrics_annotation = get_metric_annotation()
    msg_flow_metric_data = str()
    for msg_flow in message_flows:
        msg_flow_list = msg_flow.split()
        bip_code = msg_flow_list[0].replace(':', '')
        if bip_code in bip_codes.keys():
            egname = msg_flow_list[bip_codes[bip_code][1]]
            app_name = msg_flow_list[bip_codes[bip_code][2]]
            message_flow_name = msg_flow_list[bip_codes[bip_code][3]]
            status = msg_flow_list[bip_codes[bip_code][4]].replace(".", "")
            template_string = 'egname="{0}", brokername="{1}", appname="{2}", messageflowname="{3}"'.format(
                egname.replace("'", ""),
                broker_name,
                app_name.replace("'", "").replace(",", ""),
                message_flow_name.replace("'", ""))
            msg_flow_metric = '{0}{{{1}}} {2}\n'.format(
                get_metric_name(metric_label='status'),
                template_string,
                get_status(status=status))
            msg_flow_metric_data += msg_flow_metric
    if msg_flow_metric_data:
        msg_flow_metric_data = '{0}{1}'.format(
            metrics_annotation['status'],
            msg_flow_metric_data)
    return msg_flow_metric_data
