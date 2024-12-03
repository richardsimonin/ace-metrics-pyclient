# -*- coding: utf-8 -*-
"""Various functions for client api."""
import subprocess


def run_ace_command(**kwargs):
    """Calls predefined commands and returns their result."""
    command_mapping = {
        'get_integration_nodes_status': 'mqsilist | grep "Integration node"',
        'get_broker_objects': 'mqsilist {0} -r',
    }
    broker = str()
    for arg_name, arg_value in kwargs.items():
        if arg_name == 'task':
            ace_command = command_mapping[arg_value]
        elif arg_name == 'broker_name':
            broker = arg_value
    if broker:
        command = ace_command.format(broker)
    else:
        command = ace_command
    output = execute_command(command=command)
    return output


def execute_command(command):
    """Executes in shell."""
    proc = subprocess.Popen(command,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=True)
    result = proc.communicate()[0]
    return result


def get_status(status):
    """Returns a numeric status value."""
    status_map = {
        'running': 1,
        'stopped': 0}
    return status_map[status]


def get_platform_params_for_commands(ace_ver):
    """Returns parameters for internal functions depending on Integration Bus version."""
    mqsilist_integration_nodes = "get_integration_nodes_status"
    # See IBM diagnostic messages:
    # https://www.ibm.com/support/knowledgecenter/en/SSMKHH_9.0.0/com.ibm.etools.mft.bipmsgs.doc/ay_bip1.htm
    # Also you can use command: mqsiexplain <bip_code>
    # https://www.ibm.com/support/knowledgecenter/en/SSMKHH_10.0.0/com.ibm.etools.mft.bipmsgs.doc/ay_bip1.htm
    bip_codes_integration_nodes = {
        # BIPCode: [broker_name_position, qm_name_position, status_position, trim_last_dot_in_qm_name]
        'BIP1284I': [3, 8, 14, 'false'],
        'BIP1285I': [3, 7, 9, 'false'],
        'BIP1295I': [3, 19, 15, 'true'],
        'BIP1296I': [3, 24 ,5, 'true'],
        'BIP1298I': [3, 18, 5, 'true'],
        'BIP1325I': [3, None, 9, 'false'],
        'BIP1326I': [3, None, 5, 'false'],
        'BIP1340I': [3, None, 5, 'false'],
        'BIP1353I': [3, 8, 10, 'false'],
        'BIP1366I': [3, 19, 15, 'true'],
        'BIP1376I': [3, 19, 15, 'true'],
        'BIP1377I': [3, 24, 5, 'true']
    }
    bip_codes_integration_nodes_components = {
        'BIP1286I': ['exec_groups', 7, 3, 9],
        'BIP1287I': ['exec_groups', 7, 3, 9],
        'BIP1275I': ['applications', 6, 2, 8],
        'BIP1276I': ['applications', 6, 2, 8],
        'BIP1277I': ['message_flows', 7, 11, 3, 9],
        'BIP1278I': ['message_flows', 7, 11, 3, 9]}
    if ace_ver == "11":
        return mqsilist_integration_nodes, bip_codes_integration_nodes, bip_codes_integration_nodes_components
    if ace_ver == "12":
        return mqsilist_integration_nodes, bip_codes_integration_nodes, bip_codes_integration_nodes_components
