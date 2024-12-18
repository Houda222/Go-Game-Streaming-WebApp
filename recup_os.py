import platform
import os

def get_os():
    os_name = platform.system()
    
    if os_name == "Darwin":
        return "MacOS"
    elif os_name == "Windows":
        return "Windows"
    elif os_name == "Linux":
        return "Linux"
    else:
        return "Unknown OS"


