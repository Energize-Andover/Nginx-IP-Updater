import os
import subprocess


def path_join(*args):
    path = ''

    for arg in args:
        path = os.path.join(path, arg)

    return path


# Returns (out. error)
def run_command(*args):
    command_out = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    return command_out.communicate()
