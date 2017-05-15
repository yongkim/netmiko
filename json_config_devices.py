from __future__ import absolute_import, division, print_function

import netmiko
import json
import getpass
from datetime import datetime
import YesNo

netmiko_exceptions = (netmiko.ssh_exception.NetMikoTimeoutException,
					  netmiko.ssh_exception.NetMikoAuthenticationException)

netmiko_failed_devices = []

#Prompt for username and password; using getpass module so password is not echoed in prompt
#Password is also verified to make sure it is being typed correctly
user = input('Username:')
passwd = None
while not passwd:
	passwd = getpass.getpass('Password for ' + user + ':')
	passwd_verify = getpass.getpass('Confirm your password: ')
	if passwd != passwd_verify:
		print('Passwords do not match. Try again.')
		passwd = None

#Uncomment to test username and password
#print(user, passwd)

print('\nGot username and password. Gathering device details...')

#Open the file devices.json which is a list of dictionaries containing device types and ip addresses.
#List of dictionaries will be passed into netmiko module which handles the SSH connections.
with open('devices.json') as dev_file:
	devices = json.load(dev_file)
"""
#Prompt for Yes or No to move on. If no, exit the script. If yes, move onto clearing NHRP mapping. Default is yes.
answer = YesNo.query_yes_no('Device details gathered. Move onto clearing NHRP mappings?', default='yes')
if answer == 'no':
	print('Quitting...')
	print('BYE!')
	quit()
elif answer == 'yes':
	print('\nClearing NHRP mappings on each device in the list...')
"""
#Log start time of this part of the script, will be used later to calculate total time.
start_time = datetime.now()
#Loop through each device from the devices.json file. Username and Password are passed from the input earlier.
#Connect to the device, gather before data, run commands, gather after data. Disconnect from the device.
#If there are auth or timeout exceptions, print the reason and log the device name.
for device in devices:
	device['username'] = user
	device['password'] = passwd
	device['secret'] = passwd
	try:
		print('~'*79)
		print('\nConnecting to device', device['ip'])
		net_connect = netmiko.ConnectHandler(**device)
		net_connect.enable()
		print('\nGathering output of show dmvpn peer tunnel 10.100.122.2 on', device['ip'])
		output = net_connect.send_command('show dmvpn peer tunnel 10.100.122.2')
		print('\n~~~~~~ Device {0} BEFORE ~~~~~~'.format(device['ip']))
		print(output)
		print('\nSending clear ip nhrp 10.100.122.2 on', device['ip'])
		net_connect.send_command('clear ip nhrp 10.100.122.2')
		print('Command sent')
		print('\nGathering output of show dmvpn peer tunnel 10.100.122.2 on', device['ip'])
		output = net_connect.send_command('show dmvpn peer tunnel 10.100.122.2')
		print('\n~~~~~~ Device {0} AFTER ~~~~~~'.format(device['ip']))
		print(output)
		print('\nDisconnecting from', device['ip'])
		net_connect.disconnect()
		print('\n~~~~~~ END ~~~~~~\n')
	except netmiko_exceptions as e:
		print('\nConnection failed.', e)
		netmiko_failed_devices.append(str(device['ip']))

end_time = datetime.now()
total_time = end_time - start_time

print('Total time for clearing NHRP mappings:', total_time)
"""
#Prompt for Yes or No to move on. If no, exit the script. If yes, move onto clearing NHRP mapping. Default is yes.
answer = YesNo.query_yes_no('NHRP mappings cleared. Move onto mapping new static NHRP map on Tunnel10?', default='yes')
if answer == 'no':
	print('Quitting...')
	print('BYE!')
	quit()
elif answer == 'yes':
	print('Setting new static NHRP mappings on Tunnel 10 of each device in the list...')
"""
#Define the list of commands to run in net_connect.send_config_set(commands)
commands = ['interface tunnel10', 'no ip nhrp map multicast 10.100.90.5', 'no ip nhrp map 10.100.122.2 10.100.90.5', 'ip nhrp map multicast 10.100.92.5', 'ip nhrp map 10.100.122.2 10.100.92.5']

start_time = datetime.now()
for device in devices:
	device['username'] = user
	device['password'] = passwd
	device['secret'] = passwd
	try:
		print('~'*79)
		print('\nConnecting to device ', device['ip'])
		net_connect = netmiko.ConnectHandler(**device)
		net_connect.enable()
		print('\nGathering output of show run interface tunnel10 on', device['ip'])
		output = net_connect.send_command('show run interface tunnel10')
		print('\n~~~~~~ Device {0} BEFORE ~~~~~~'.format(device['ip']))
		print(output)
		print('\nSetting new NHRP mappings on tunnel 10 of', device['ip'])
		net_connect.send_config_set(commands)
		print('Commands sent')
		print('\nGathering output of show run interface tunnel10 on', device['ip'])
		output = net_connect.send_command('show run interface tunnel10')
		print('\n~~~~~~ Device {0} AFTER ~~~~~~'.format(device['ip']))
		print(output)
		answer = YesNo.query_yes_no('\nSave configuration?', default='yes')
		if answer == 'no':
			print('Quitting...')
			print('BYE!')
			net_connect.disconnect()
			quit()
		elif answer == 'yes':
			print('\nSaving configuration...')
			net_connect.send_command_expect('write mem')
			print('\nSaved.')
		print('\nDisconnecting from', device['ip'])
		net_connect.disconnect()
		print('\n~~~~~~ END ~~~~~~\n')
	except netmiko_exceptions as e:
		print('\nConnection failed.', e)
		netmiko_failed_devices.append(str(device['ip']))

end_time = datetime.now()
total_time = end_time - start_time

print('Total time for setting NHRP mappings: ', total_time)

#Print a list of devices - without duplicates - for which the script did not run.
print('\nFailed to connect to the following devices:\n')
failed_devices_nodups = list(set(netmiko_failed_devices))
print(failed_devices_nodups)

print('\nALL DONE! Please continue the maintenance.')
