import mitmproxy
import os
from datetime import datetime

def request(flow):
    # get parent directory 
    path = os.getcwd() + "/../"
    # get all files in parent
    files = os.listdir(path)
    # get all paths of .txt files
    paths = [os.path.join(path, basename) for basename in files if basename.startswith('applicationlog_')]
    if paths:
        # get latest .txt file (the one to be sent via email)
        filename = max(paths, key=os.path.getctime)
        with open(filename, 'a') as f: 
            curr_time = datetime.now().strftime("%H:%M:%S")
            f.write("[" + curr_time + "] " + flow.request.pretty_url + '\n')
            print("Sucessfully written")
    else:
        # create new log file if no previous log file exists
        filename = path + "applicationlog_" + datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + ".txt"
        with open(filename, 'w+') as f: 
            curr_time = datetime.now().strftime("%H:%M:%S")
            f.write("[" + curr_time + "] " + flow.request.pretty_url + '\n')
            print("Sucessfully written")
