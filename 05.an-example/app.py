from flask import Flask, render_template, request
import scapy.all as scapy
import datetime
import binascii
import re
import json
import copy

# This was hacked together in a few hours so there is plenty of room for improvement 
# however it should provide a good starting point
# 

app = Flask(__name__)

# these are the filters that are available in the drop down menu
FILTERS = ['icmp','tcp','udp']

HEADER_FORMAT = [
            {"field_category":"Ethernet", "field_name":"Destination MAC","octets":6, "bits":48,"field_url":"https://en.wikipedia.org/wiki/Ethernet_frame"},
            {"field_category":"Ethernet", "field_name":"Source MAC","octets":6, "bits":48,"field_url":"https://en.wikipedia.org/wiki/Ethernet_frame"},
            {"field_category":"Ethernet", "field_name":"EtherType","octets":2, "bits":16,"field_url":"https://en.wikipedia.org/wiki/EtherType"},
            {"field_category":"IP", "field_name":"IP Version (4 bits) / Internet Header Length (4 bits)","octets":1,"bits":8,"field_url":"https://en.wikipedia.org/wiki/Internet_Protocol_version_4"},
            {"field_category":"IP", "field_name":"DSCP (6 bits) / ECN (2 bits)","octets":1,"bits":8,"field_url":"https://en.wikipedia.org/wiki/Internet_Protocol_version_4"},
            {"field_category":"IP", "field_name":"Total Length","octets":2,"bits":16,"field_url":"https://en.wikipedia.org/wiki/Internet_Protocol_version_4"},
            {"field_category":"IP", "field_name":"Identification","octets":2,"bits":16,"field_url":"https://en.wikipedia.org/wiki/Internet_Protocol_version_4"},
            {"field_category":"IP", "field_name":"Flags and Fragment Offset","octets":2,"bits":16,"field_url":"https://en.wikipedia.org/wiki/Internet_Protocol_version_4"},
            {"field_category":"IP", "field_name":"Time To Live (TTL)","octets":1,"bits":8,"field_url":"https://en.wikipedia.org/wiki/Internet_Protocol_version_4"},
            {"field_category":"IP", "field_name":"Protocol","octets":1,"bits":8,"field_url":"https://en.wikipedia.org/wiki/Internet_Protocol_version_4"},
            {"field_category":"IP", "field_name":"Checksum","octets":2,"bits":16,"field_url":"https://en.wikipedia.org/wiki/Internet_Protocol_version_4"},
            {"field_category":"IP", "field_name":"Source IP","octets":4,"bits":32,"field_url":"https://en.wikipedia.org/wiki/Internet_Protocol_version_4"},
            {"field_category":"IP", "field_name":"Destination IP","octets":4,"bits":32,"field_url":"https://en.wikipedia.org/wiki/Internet_Protocol_version_4"},
            {"field_category":"icmp", "field_name":"ICMP Type","octets":1,"bits":8,"field_url":"https://en.wikipedia.org/wiki/Internet_Control_Message_Protocol"},
            {"field_category":"icmp", "field_name":"ICMP Code","octets":1,"bits":8,"field_url":"https://en.wikipedia.org/wiki/Internet_Control_Message_Protocol"},
            {"field_category":"icmp", "field_name":"Checksum","octets":2,"bits":16,"field_url":"https://en.wikipedia.org/wiki/Internet_Control_Message_Protocol"},
            {"field_category":"tcp", "field_name":"Source Port","octets":2,"bits":16,"field_url":"https://en.wikipedia.org/wiki/Transmission_Control_Protocol"},
            {"field_category":"tcp", "field_name":"Destination Port","octets":2,"bits":16,"field_url":"https://en.wikipedia.org/wiki/Transmission_Control_Protocol"},
            {"field_category":"tcp", "field_name":"Sequence Number","octets": 4,"bits":32,"field_url":"https://en.wikipedia.org/wiki/Transmission_Control_Protocol"},
            {"field_category":"tcp", "field_name":"Acknowledgement","octets":4,"bits":32,"field_url":"https://en.wikipedia.org/wiki/Transmission_Control_Protocol"},
            {"field_category":"udp", "field_name":"Source Port","octets":2,"bits":16,"field_url":"https://en.wikipedia.org/wiki/User_Datagram_Protocol"},
            {"field_category":"udp", "field_name":"Destination Port","octets":2,"bits":16,"field_url":"https://en.wikipedia.org/wiki/User_Datagram_Protocol"},
            {"field_category":"udp", "field_name":"Length","octets": 2,"bits":16,"field_url": "https://en.wikipedia.org/wiki/User_Datagram_Protocol"},
            {"field_category":"udp", "field_name":"Checksum","octets":2,"bits":16,"field_url":"https://en.wikipedia.org/wiki/User_Datagram_Protocol"},
        ]

@app.route('/')
def hello():
    return render_template('index.html', utc_dt=datetime.datetime.utcnow(),\
                                        interfaces=scapy.get_if_list(), \
                                        filters=FILTERS)

@app.route('/generate_monitoring_report',methods=['GET','POST'])
def generate_monitoring_report():

    # this will get the value that was selected in the drop down menu
    selected_interface = request.args.get('select-interfaces')
    selected_filter = request.args.get('select-filter')
    selected_packet_count = int(request.args.get('select-packet-count'))

    # this is the line which captures the traffic using the scapy library
    try: 
        packets = scapy.sniff(iface=selected_interface, filter=selected_filter, count=selected_packet_count)
    except Exception as e:
        return render_template('error.html',error=str(e))
        

    all_packets = []
    
    for idx, packet in enumerate(packets):

        #print(packet.show(dump=True))
        
        # creates a list with each element consisting of two hex characters (one octet/byte) from the scapy hex output
        # e.g. 3c846a9d3a84 becomes ['3c', '84', '6a', '9d', '3a', '84']
        # will be used to highlight the header format
        
        hex_dump = re.findall('..',scapy.raw(packet).hex())

        # creates a string representing the packet capture in binary
        # [2:] removes the 0b from the binary string at the start. As per the following link, this is how Python tells you 
        # what base the number is. 
        # Base 2 uses 0b 
        # Base 16 uses 0x
        # Base 8 uses 0.
        # https://stackoverflow.com/questions/46002161/what-does-the-0b-mean-at-the-begining-of-the-byte-0b1100010
        # 
        # 00 is prepended and replaces the 0b

        binary_dump = f"00{bin(int.from_bytes(scapy.raw(packet)))[2:]}" 

        # these are used below to calculate which octets/bits are displayed in each column of the table
        previous_field_end_octets = 0
        current_field_end_octets = 0

        previous_field_end_bits = 0
        current_field_end_bits = 0

        formatted_packet_header = []
        
        # This next section formats the data which will be displayed in the table
        # 1. Loop through each field in the HEADER
        # 2. Add the field to a new list
        # 3. Calculate which hex and binary represent this field 
        # by selecting the [previous_field_end_octets:current_field_end_octets]
        # 4. Append this data to the last element of new list (formatted_packet_header[-1]["field_data_hex"] = current_field_data)
        # 5. Do this first for hex and then for binary
        

        for field in HEADER_FORMAT:
            
            # Only want to add the relevant fields to the table so need to check if they the correct filter (or Ethernet/IP)
            # i.e. we shouldn't show TCP columns if UDP was selected
            #
            # I came across this interesting way to check for the rules instead of using if 'a 'or 'b' or 'c'
            # https://stackoverflow.com/a/50656647
            # 

            # if (field["field_category"] == "Ethernet" 
            #         or field["field_category"] == "IP" 
            #             or field["field_category"] == selected_filter):
            
            RULES = [
                    field["field_category"] == "Ethernet",
                    field["field_category"] == "IP" ,
                    field["field_category"] == selected_filter
            ]

            if any(RULES):
                formatted_packet_header.append(field) 
        
                # Hex formatting
                current_field_length_octets = field["octets"]
                current_field_end_octets = previous_field_end_octets + current_field_length_octets
                current_field_data = " ".join(hex_dump[previous_field_end_octets:current_field_end_octets])
                formatted_packet_header[-1]["field_data_hex"] = current_field_data   
                previous_field_end_octets += field["octets"]

                # Binary formatting
                current_field_length_bits = field["bits"]
                current_field_end_bits = previous_field_end_bits + current_field_length_bits
                current_field_data_binary = (' ').join(re.findall('.{1,8}',binary_dump[previous_field_end_bits:current_field_end_bits]))
                formatted_packet_header[-1]["field_data_binary"] = current_field_data_binary 
                previous_field_end_bits += field["bits"]
        
        # Capture all the packet information which is then sent to the HTML page and displayed
        all_packets.append({"packet_number":idx,"packet_readable": packet, "packet_payload": packet.payload,"raw_hex":' '.join(hex_dump), \
                                    "raw_binary":' '.join(re.findall('.{1,8}',binary_dump)), "formatted_packet_header": copy.deepcopy(formatted_packet_header) \
                            })
        
    return render_template('monitoring_report.html', utc_dt=datetime.datetime.utcnow(),\
                        selected_interface=selected_interface,selected_filter=selected_filter, all_packets=all_packets)

if __name__ == '__main__':
    app.run(port=33000, debug=True)