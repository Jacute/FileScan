import os.path
import sys

from mega import Mega, errors
from config import email, password
from threading import Thread
import socket
import schedule
import time
import re
import win32api
import win32con
import shutil
from progress.bar import IncrementalBar
import colorama
from colorama import Fore


def check_internet():
    try:
        print(Fore.WHITE + "Checking internet connection...\n")
        host = socket.gethostbyname("www.google.com")
        s = socket.create_connection((host, 80), 2)
        s.close()
        print(Fore.GREEN + 'Internet on\n')
        return True
    except Exception:
        print(Fore.RED + "Internet off\n")
        return False


def upload_files(files=None):
    if check_internet():
        if files:
            print(Fore.WHITE + 'Uploading files...')
            bar = IncrementalBar('Countdown', max=len(files))
            for file in files:
                bar.next()
                m.upload(file)
            print(Fore.GREEN + '\nFiles upload success\n')
        else:
            if os.listdir(DIR):
                print(Fore.WHITE + 'Uploading files...')
                bar = IncrementalBar('Countdown', max=len(os.listdir(DIR)))
                for file in os.listdir(DIR):
                    bar.next()
                    m.upload(DIR + '\\' + file)
                    os.remove(DIR + '\\' + file)
                print(Fore.GREEN + '\nFiles upload success\n')
            print('Enter file name: ')


def find_file(root_folder, rex):
    lst = list()
    for root, dirs, files in os.walk(root_folder):
        for f in files:
            result = rex.search(f)
            if result and '.FileScanData' not in os.path.join(root, f):
                lst.append(os.path.join(root, f))
                print(Fore.CYAN + os.path.join(root, f))
    return lst


def copy_files(files):
    print(Fore.WHITE + 'Copying files...')
    for file in files:
        fullName = file.split('\\')[-1]
        if fullName in os.listdir(DIR):
            shutil.copyfile(file, 'C:\\.FileScanData\\{}'.format(str(os.listdir("C:\\.FileScanData").count(fullName)) +
                                                                 fullName))
        else:
            shutil.copyfile(file, 'C:\\.FileScanData\\{}'.format(fullName))
    print(Fore.GREEN + '\nFiles copied success\n')


def search():
    while True:
        files = list()
        print('Enter file name: ')
        fileName = input()
        rex = re.compile(fileName)

        for drive in win32api.GetLogicalDriveStrings().split('\000')[:-1]:
            files.extend(find_file(drive, rex))

        if check_internet():
            upload_files(files)
        else:
            copy_files(files)


def schedule_proc():
    while True:
        schedule.run_pending()
        time.sleep(0.1)


if __name__ == '__main__':
    DIR = 'C:\\.FileScanData'

    mega = Mega()
    colorama.init(autoreset=True)

    if '.FileScanData' not in os.listdir('C:\\'):
        os.mkdir(DIR)
        win32api.SetFileAttributes(DIR, win32con.FILE_ATTRIBUTE_HIDDEN)
    try:
        m = mega.login(email, password)
    except errors.RequestError:
        print(Fore.RED + "Auth error!")
        sys.exit()
    except Exception:
        print(Fore.RED + "Mega connection error!")
        sys.exit()

    schedule.every(5).minutes.do(upload_files)
    Thread(target=schedule_proc).start()
    Thread(target=search).start()
