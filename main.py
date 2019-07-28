import time
import sys
from helpers import *
from secrets import *


def get_inet_ip():
    net_config = run_command('ifconfig', '-a')[0]
    net_config = str(net_config)

    search_string = '{0}: flags='.format(CONNECTION_NAME)
    connection_start = net_config.find(search_string)
    connection_end = net_config.find(': flags=', len(search_string))

    connection_config = net_config[connection_start:connection_end]

    inet_ip = connection_config[connection_config.find('inet') + 5:connection_config.find('netmask')].rstrip()

    return inet_ip


if __name__ == "__main__":
    last_ip = get_inet_ip()

    try:
        while True:
            current_ip = get_inet_ip()

            if current_ip != last_ip:
                print('changed')

            last_ip = current_ip
            time.sleep(60)  # Run every minute
    except KeyboardInterrupt:
        sys.exit(1)
