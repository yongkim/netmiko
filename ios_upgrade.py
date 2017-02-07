# import sys
from datetime import datetime
from getpass import getpass
from netmiko import ConnectHandler, FileTransfer

def main():
	"""Script to login to a Cisco IOS device"""
	ip_addr = input("Enter Cisco device IP address: ")
	my_pass = getpass()
	start_time= datetime.now()
	print(">>>> {}".format(start_time))
	
	net_device = {
		'device_type': 'cisco_ios',
		'ip': ip_addr,
		'username': 'neteng',
		'password': my_pass,
		'secret': my_pass,
		'port': 22,
		}
	
	print("\nLogging in to Cisco Device")
	ssh_conn = ConnectHandler(**net_device)
	print
	
	print("\nVerifying state")
	output = ssh_conn.send_command ('show ver')
	print(output)

	output = ssh_conn.send_command ('show run | inc logging')
	print(output)

	buffer_number = input("Enter logging buffer amount: ")
	config_commands = 'logging buffered {}'.format(buffer_number)
	output = ssh_conn.send_config_set([config_commands])
	print(output)

	output = ssh_conn.send_command('show run | inc logging')
	print(output)

if __name__ == "__main__":
        main()
