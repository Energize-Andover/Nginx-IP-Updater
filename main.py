import time
import sys
from helpers import *
from config import *


def get_inet_ip():
    net_config = run_command('ifconfig', '-a')[0]
    net_config = str(net_config)

    search_string = '{0}: flags='.format(NETWORK_INTERFACE)
    connection_start = net_config.find(search_string)
    connection_end = net_config.find(': flags=', connection_start + len(search_string))

    if connection_end == -1:
        connection_end = len(net_config)

    connection_config = net_config[connection_start:connection_end]

    inet_ip = connection_config[connection_config.find('inet') + 5:connection_config.find('netmask')].rstrip()

    return inet_ip


if __name__ == "__main__":

    if os.geteuid() != 0:
        print("Please run this file as administrator!")
        sys.exit(-1)

    last_ip = get_inet_ip()
    print("Now tracking inet IP address {0} in network interface {1}".format(last_ip, NETWORK_INTERFACE))

    try:
        while True:
            current_ip = get_inet_ip()

            if current_ip != last_ip:
                for file in CONF_FILE_NAMES:
                    file_path = path_join(CONFIG_FILE_FOLDER, file)

                    file_data = None

                    with open(file_path, 'r') as config_file:
                        file_data = config_file.read()

                    original_file_data = file_data

                    # Replace all instances of the old ip with the new ips
                    file_data = file_data.replace(last_ip, current_ip)

                    # Delete old config file
                    os.remove(file_path)

                    # Replace with new config file
                    with open(file_path, 'w+') as config_file:
                        config_file.write(file_data)

                    # Test config
                    test_output = run_command('sudo', 'nginx', '-t')[0].decode('UTF-8')

                    passed_test = True

                    for output_line in test_output.split('\n'):
                        if len(output_line) > 0:
                            if not output_line.endswith('is ok') and not output_line.endswith('is successful'):
                                passed_test = False
                                break

                    if not passed_test:
                        os.remove(file_path)  # Remove modified config file

                        # Restore to original state
                        with open(file_path, 'w+') as config_file:
                            config_file.write(original_file_data)

                        print("There are problems with your configuration syntax in the file " + file_path)
                        sys.exit(-1)

                    # Passed the test, restart
                    run_command('sudo', 'systemctl', 'restart', 'nginx')

            last_ip = current_ip
            time.sleep(60)  # Run every minute
    except KeyboardInterrupt:
        sys.exit(-1)
