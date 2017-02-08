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
        
        print("\nView software version")
        output = ssh_conn.send_command ('show ver')
        print(output)

        # This can be used to send any command/configs
        """output = ssh_conn.send_command ('show run | inc logging')
        print(output)

        buffer_number = input("Enter logging buffer amount: ")
        config_commands = 'logging buffered {}'.format(buffer_number)
        output = ssh_conn.send_config_set([config_commands])
        print(output)

        output = ssh_conn.send_command('show run | inc logging')
        print(output)"""
        
        # Image file settings
        dest_file_system = 'bootflash:'
        source_file = 'something\\asr1000-universalk9.16.04.01.SPA.bin' # Use absolute path
        dest_file = 'asr1000-universalk9.16.04.01.SPA.bin' 

        with FileTransfer(ssh_conn, source_file=source_file, dest_file=dest_file, file_system=dest_file_system) as scp_transfer:
                if not scp_transfer.check_file_exists():
                        if not scp_transfer.verify_space_available():
                                raise ValuError("Insufficient space available on remote device")

                        print("Transferring file\n")
                        scp_transfer.transfer_file()

                print("\nVerifying file")
                if scp_transfer.verify_file():
                        print("Source and destination MD5 hash match")
                else:
                        raise ValueError("MD5 hash between source and destination do not match")

        print("\nSending boot commands")
        full_file_name = "{}/{}".format(dest_file_system, dest_file)
        boot_cmd = "boot system flash {}".format(full_file_name)
        output = ssh_conn.send_config_set([boot_cmd])
        print(output)
        
        print("\nWrite mem")
        output = ssh_conn.send_command('write mem')
        print(output)
        
        print("\nVerifying state")
        output = ssh_conn.send_command('show boot')
        print(output)

        print("\nReload")
        output = ssh_conn.send_command_timing('reload')
        output += ssh_conn.send_command_timing('y')
        print(output)
        
        print("\n>>>> {}".format(datetime.now() - start_time))
        print("\n")

if __name__ == "__main__":
        main()
