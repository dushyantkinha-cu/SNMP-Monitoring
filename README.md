# Automated SNMP Data Collection and CPU Monitoring for Cisco IOS

This repository contains a Python-based network automation solution designed to query multiple Cisco IOS routers using the Simple Network Management Protocol (SNMP). By utilizing centralized inventory files and modular scripts, this project demonstrates foundational Infrastructure as Code (IaC) principles to efficiently extract, format, and visualize critical network data.

## Features

* **Comprehensive Data Retrieval:** Utilizes `pysnmp` to walk specific OIDs across multiple devices, gathering interface descriptions, operational statuses, and assigned IPv4/IPv6 addresses.
* **Centralized Inventory Management:** Reads device connection parameters (IP addresses, credentials) from a structured JSON file, separating configuration from the execution logic.
* **Data Aggregation and Export:** Correlates the retrieved SNMP data and exports a consolidated, human-readable JSON payload containing both interface addressing and status information.
* **Real-time CPU Monitoring and Visualization:** Specifically targets a designated router to poll CPU utilization at 5-second intervals over a 2-minute period. The collected data is then plotted and saved as a line graph using `matplotlib`.

## File Structure

* **`NMsnmp.py`**: The primary execution script. It orchestrates the SNMP walks to gather interface data (names, statuses, IPv4, and IPv6 addresses) across all devices. It also contains the logic to monitor CPU utilization on a specific device and generate a visual graph.
* **`sshInfo.py`**: A utility script responsible for securely loading the device inventory from the JSON file.
* **`sshInfo.json`**: The inventory file containing device hostnames, IP addresses, types, and authentication credentials.

## Prerequisites

* Python 3.x
* `pysnmp` (`pip install pysnmp`)
* `matplotlib` (`pip install matplotlib`)
* Network reachability to the target Cisco IOS devices.
* SNMP (v1/v2c) enabled on the target devices with the community string "public" (can be adjusted in `NMsnmp.py`).

## Usage

1.  Update `sshInfo.json` with your specific target router IPs and credentials.
2.  Ensure SNMP is configured on your target devices with the appropriate community string.
3.  Execute the main script:
```bash
python NMsnmp.py
