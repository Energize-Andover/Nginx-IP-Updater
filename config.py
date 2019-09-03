import os

'''
    # Utilize the os package to form your paths:
    # The method os.path.join(part1, part2, ... lastPart) forms a properly-formatted path for your OS.
    # The variable os.sep represents the proper path separator for your os (i.e. '/')
'''

# The path to the folder in which the machine's nginx configuration files lie (e.g. /etc/nginx/conf.d)
CONFIG_FILE_FOLDER = os.path.join(os.sep, 'etc', 'nginx', 'conf.d')

# The list of the names of the .conf files in CONFIG_FILE_FOLDER to update upon inet IP change
CONF_FILE_NAMES = ['virtual.conf']  # Format: ['name.conf', 'name2.conf', ... 'lastName.conf']

# The name of the network interface in which your inet ip address is broadcast (e.g. 'wlan0')
NETWORK_INTERFACE = 'wlp5s0'

'''
  # Do NOT delete or rename any of these configuration constants. Doing so will stop the IP Updater from running.
  # BE SURE TO RUN 'git update-index --skip-worktree config.py' in the command line AFTER MAKING CHANGES TO THIS FILE FOR THE
    FIRST TIME! Doing so will keep your machine-specific configurations out of the repository, allowing the defaults to
    remain untouched.
'''
