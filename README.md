# IBM ACE metrics exporter

[![Actions Status](https://github.com/AATools/ib-metrics-pyclient/workflows/GitHub%20CI/badge.svg)](https://github.com/AATools/ib-metrics-pyclient/actions) [![Coverage Status](https://coveralls.io/repos/github/AATools/ib-metrics-pyclient/badge.svg?branch=master)](https://coveralls.io/github/AATools/ib-metrics-pyclient?branch=master)

This is python client for collecting IBM Integration Bus metrics and exporting to [Prometheus pushgateway](https://github.com/prometheus/pushgateway).
The collected metrics can be explored in Prometheus or Grafana.

The metrics are collected by using [mqsilist](https://www.ibm.com/docs/en/app-connect/12.0?topic=commands-mqsilist-command) command. The metrics are collected for **all local** Brokers. You need to run `IB metrics pyclient` in the same host where `IBM Integration Bus` was installed.

Tested for IBM ACE v11 and v12 and Python 3.6, 3.7 on Linux.

## Collected metrics

By default, metrics are collected every 60 seconds.

The metrics provided by the client:

* `ace_broker_status...` - current status of ACE broker;
* `ace_exec_group_status...` - current status of ACE execution group;
* `ace_application_status...` - current status of ACE application;
* `ace_message_flow_status...` -  current status of ACE message flow.

See [detailed description of the metrics](#metrics-detailed-description) for an in-depth understanding.

## Getting Started

Download Prometheus Pushgateway from the [release page](https://github.com/prometheus/pushgateway/releases) and unpack the tarball.

### Run Prometheus Pushgateway

```bash
cd pushgateway
nohup ./pushgateway > pushgateway.log &
```

For Pushgateway the default port is used (":9091").

### Run ace-metrics-pyclient

```bash
git clone https://github.com/richardsimonin/ace-metrics-pyclient
cd ace-metrics-pyclient
nohup python3 ace_metrics_client.py &
```

After that, you should set up your Prometheus server to collect metrics from Pushgateway (`http://<hostname>:9091/metrics`).

You can specify `host` and `port` for pushgateway, Integration Bus version and time interval in seconds between collecting metrics via command-line arguments.

```bash
python3 ace_metrics_client.py -h

usage: ace_metrics_client.py [-h] [--pghost [pushgatewayHost]] [--pgport [pushgatewayPort]] [--acever [aceVersion]] [--collectint [collectInterval]]

optional arguments:
  -h, --help            show this help message and exit
  --pghost [pushgatewayHost]
                        pushgateway host
  --pgport [pushgatewayPort]
                        pushgateway port
  --acever [aceVersion]
                        ACE version: 11 or 12
  --collectint [collectInterval]
                        time interval between collecting metrics
```

If argument is not set the default value is used.

| Command-line argument | Description | Default value |
|:---|:---|:---|
| `pghost` | Pushgateway host | Hostname on which client is started.<br> Value define via `platform.node()`. |
| `pgport` | Pushgateway port | `9091` |
| `acever` | ACE version | `12`<br> Valid value: **9** or **10**.<br> If argument is omitted or invalid value is passed, the client will try to determine version via environment variable `MQSI_VERSION_V`. If it can't determine the version using the environment variable, the default value will be used. |
| `collectint` | Time interval between collecting metrics | `60` <br> Time in seconds. |


## Metrics detailed description

| Metric | Description |
|:---|:---|
| ace_broker_status | The metric shows current status of ACE broker.<br> Metric type: `gauge`.<br> If there are several brokers on host, there will be a own metric for each broker.<br> Possible values:<br> <span style="margin-left:2em">`0` - STOPPED;</span><br> <span style="margin-left:2em">`1` - RUNNING.</span><br> Example display in Pushgateway:<br> `ace_broker_status{brokername="BRK1",instance="",job="BRK1",qmname="QM1"} 1` |
| ace_exec_group_status | The metric shows current status of ACE execution group.<br> Metric type: `gauge`.<br> If there are several execution groups on host, there will be a own metric for each execution group.<br> Possible values:<br> <span style="margin-left:2em">`0` - STOPPED;</span><br> <span style="margin-left:2em">`1` - RUNNING.</span><br> Example display in Pushgateway:<br> `ace_exec_group_status{brokername="BRK1",egname="EG1",instance="",job="BRK1"} 1` |
| ace_application_status | The metric shows current status of ACE application.<br> Metric type: `gauge`.<br> If there are several applications on host, there will be a own metric for each application.<br> Possible values:<br> <span style="margin-left:2em">`0` - STOPPED;</span><br> <span style="margin-left:2em">`1` - RUNNING.</span><br> Example display in Pushgateway:<br> `ace_application_status{appname="Application1",brokername="BRK1",egname="EG1",instance="",job="BRK1"} 1` |
| ace_message_flow_status | The metric shows current status of ACE message flow.<br> Metric type: `gauge`.<br> If there are several message flows on host, there will be a own metric for each message flow.<br> Possible values:<br> <span style="margin-left:2em">`0` - STOPPED;</span><br> <span style="margin-left:2em">`1` - RUNNING.</span><br> Example display in Pushgateway:<br> `ace_message_flow_status{appname="Application1",brokername="BRK1",egname="EG1",instance="",job="BRK1",messageflowname="adapter.reply"} 1` |
