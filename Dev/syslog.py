import os
import sys
import time
import colorama


class Syslog:
    def __init__(self, log_file=None):
        self.log_file = log_file
        colorama.init(autoreset=True)

    def log(self, message, level="INFO"):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        formatted_message = f"{timestamp} [{level}] {message}"

        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write(formatted_message + '\n')

        if level == "ERROR":
            print(colorama.Fore.RED + formatted_message)
        elif level == "WARNING":
            print(colorama.Fore.YELLOW + formatted_message)
        else:
            print(colorama.Fore.GREEN + formatted_message)