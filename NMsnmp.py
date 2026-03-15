import json
import time
import matplotlib.pyplot as plt
from pysnmp.hlapi import *
from sshInfo import load_devices

def snmp_walk(ip, community, oid):
    # This will walk an OID and returns a list of values
    results = []
    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=1),
        UdpTransportTarget((ip, 161), timeout=2.0, retries=2),
        ContextData(), 
        ObjectType(ObjectIdentity(oid)),
        lexicographicMode=False):
        if errorIndication or errorStatus:
            continue
        for varBind in varBinds:
            results.append((str(varBind[0]), varBind[1]))
    return results

def cpu_graph(devices, COMMUNITY_STRING):
    # This will fetch the CPU utilization and plot it
    OID_CPU = "1.3.6.1.4.1.9.9.109.1.1.1.1.3.1" 

    r1_ip = devices["R1"]["host"]
    cpu_utilization = []
    iterations = 24  # 2 minutes / 5 seconds = 24 intervals
    print(f"\nMonitoring R1 CPU utilization for 2 mins at an interval of 5s)")
    
    snmp_engine = SnmpEngine()
    for i in range(iterations):
        iterator = getCmd(
            snmp_engine,
            CommunityData(COMMUNITY_STRING, mpModel=1),
            UdpTransportTarget((r1_ip, 161), timeout=2.0, retries=2),
            ContextData(),
            ObjectType(ObjectIdentity(OID_CPU))
        )
        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
        
        # If there's an error, it will record 0. Otherwise, it will record the CPU value
        if errorIndication or errorStatus:
            cpu_val = 0
        else:
            cpu_val = int(varBinds[0][1])

        cpu_utilization.append(cpu_val)
        print(f"[{i+1}/{iterations}] CPU: {cpu_val}%")
        time.sleep(5)
    
    # This plots the graph & saves a .jpg file
    print(f"\nGenerating line graph and saving to cpu_R1.jpg")
    plt.figure(figsize=(10, 5))
    plt.plot(range(0, 120, 5), cpu_utilization, marker='o', linestyle='-', color='b')
    plt.title("R1 CPU Utilization (5-Second Average)")
    plt.xlabel("Time (Seconds)")
    plt.ylabel("CPU Utilization (%)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("cpu_R1.jpg", format="jpg")
    print("Done!")

def format_ipv6(decimal_list):
    # This converts a list of 16 decimal strings from an OID into a standard IPv6 string
    hex_parts = [f"{int(x):02x}" for x in decimal_list]
    blocks = [hex_parts[i] + hex_parts[i+1] for i in range(0, 16, 2)]
    return ":".join(blocks)

def snmp():
    OID_IF_DESCR = "1.3.6.1.2.1.2.2.1.2"             # Interface Name
    OID_IF_STATUS = "1.3.6.1.2.1.2.2.1.8"            # Interface Status (where 1=up & 2=down)
    OID_IPV4_IFINDEX = "1.3.6.1.2.1.4.20.1.2"        # IPv4 Address table
    OID_IPV6_IFINDEX = "1.3.6.1.2.1.4.34.1.3.2.16"   # IPv6 Address table

    COMMUNITY_STRING = "public"
    devices = load_devices("sshInfo.json")
    all_addresses = {}
    all_statuses = {}
    
    print("Fetching SNMP data from routers")
    
    for device_name, device_params in devices.items():
        ip = device_params["host"]
        print(f"Processing {device_name} ({ip})")
        
        # This creates the data structures for this router
        all_addresses[device_name] = {"addresses": {}}
        all_statuses[device_name] = {}
        if_map = {}
        
        # This fethces all the interfaces and builds an index_to_name mapping
        if_descr_data = snmp_walk(ip, COMMUNITY_STRING, OID_IF_DESCR)
        for oid_str, val in if_descr_data:
            if_index = oid_str.split('.')[-1]
            if_name = str(val)
            if_map[if_index] = if_name
            all_addresses[device_name]["addresses"][if_name] = {"v4": "None", "v6": "None"}
        
        # This fetches the interface statuses
        if_status_data = snmp_walk(ip, COMMUNITY_STRING, OID_IF_STATUS)
        for oid_str, val in if_status_data:
            if_index = oid_str.split('.')[-1]
            if_name = if_map.get(if_index, "Unknown")
            status_str = "up" if int(val) == 1 else "down"
            all_statuses[device_name][if_name] = status_str
    
        # This fetches the IPv4 Addresses
        ipv4_data = snmp_walk(ip, COMMUNITY_STRING, OID_IPV4_IFINDEX)
        for oid_str, val in ipv4_data:
            if_index = str(val)
            if_name = if_map.get(if_index)
            # The IPv4 address is the last 4 octets of the OID
            ipv4_addr = ".".join(oid_str.split('.')[-4:])
            all_addresses[device_name]["addresses"][if_name]["v4"] = ipv4_addr
    
        # This fetches the IPv6 Addresses
        ipv6_data = snmp_walk(ip, COMMUNITY_STRING, OID_IPV6_IFINDEX)
        for oid_str, val in ipv6_data:
            if_index = str(val)
            if_name = if_map.get(if_index)
            # The IPv6 address is the last 16 octets of the OID
            ipv6_decimals = oid_str.split('.')[-16:]
            if len(ipv6_decimals) == 16 and if_name:
                ipv6_addr = format_ipv6(ipv6_decimals)
                all_addresses[device_name]["addresses"][if_name]["v6"] = ipv6_addr
    
    # This stores both sets of data in a single JSON-formatted .txt file
    print(f"\nWriting results to snmp_data.txt")
    combined_output = {"Address_Data": all_addresses,"Status_Data": all_statuses}
    with open("snmp_data.txt", "w") as f:
        json.dump(combined_output, f, indent=4)
    
    cpu_graph(devices, COMMUNITY_STRING)

def main():
    snmp()

if __name__ == "__main__":
    main()