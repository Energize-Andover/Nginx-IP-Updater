import time
import sys
import smtplib
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
    valid_email_information = False
    server = None

    if SMTP_PORT is not None and SMTP_SERVER is not None and SERVER_EMAIL is not None and SERVER_PASSWORD is not None and RECIPIENTS is not None and len(
            RECIPIENTS) > 0 and SUBJECT is not None:
        # All information supplied, test it
        print("Attempting login to mail server...")

        print("Setting up SMTP...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.ehlo()
        server.starttls()
        print("Success!")

        print("Attempting login...")
        server.login(SERVER_EMAIL, SERVER_PASSWORD)
        server.ehlo()

        print('Success!')

        print("Mail server successfully set up")
        valid_email_information = True

    if not valid_email_information:
        print("Invalid email information! Email logging will be disabled this session!")

    if os.geteuid() != 0:
        print("Please run this file as administrator!")
        sys.exit(-1)

    try:
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

                        # Send email to configured admins from configured email, if configured properly
                        if valid_email_information:
                            #message = "From: %s\r\nTo: %s\r\n\r\n" % (SERVER_EMAIL, ", ".join(RECIPIENTS))
                            message = 'Subject: {0}\n\n'.format(SUBJECT)
                            message += 'The inet IP address in the {0} network interface of your server has changed from {1} to {2}!'.format(
                                NETWORK_INTERFACE, last_ip, current_ip)
                            server.sendmail(SERVER_EMAIL, RECIPIENTS, message)

                last_ip = current_ip
                time.sleep(60)  # Run every minute
        except KeyboardInterrupt:
            sys.exit(-1)
    except:
        if valid_email_information:
            print("Logging out of email...")
            server.quit()
        sys.exit(-1)
