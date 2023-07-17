import os
import shutil
import hashlib
import datetime
import time
from pathlib import Path
import re


# console and log print function
def log_row(action_txt, f_object):
    test_dir_path(log_path)  # check dir
    if not os.path.exists(os.path.join(log_path, "SyncVeeam.log")):  # check file
        with open(os.path.join(log_path, "SyncVeeam.log"), "w", encoding='utf-8'):  # create log file
            pass
    formatted_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S.%f")
    msg = "{0:<23} | {1:<14} | {2:<120}".format(formatted_time, action_txt, f_object)
    print(msg)
    with open(os.path.join(log_path, "SyncVeeam.log"), "a", encoding='utf-8') as file:
        file.write(msg + "\n")


# Check if the directory path exists and make required action
def test_dir_path(test_path, delete=False):
    if not os.path.exists(test_path):
        if delete:  # delete no needed
            reverse_path = test_path.replace(source_path, replica_path)  # take same path in replica
            shutil.rmtree(reverse_path, ignore_errors=True)
            log_row("remove", reverse_path)
        else:  # create missed
            if test_path != '':
                os.makedirs(test_path, exist_ok=True)
                log_row("create folder", test_path)


# copy function from source to replica (recursive)
def add_missed_items(curr_folder):
    if len(curr_folder) != 0:
        for dir_file in curr_folder:
            if os.path.isdir(dir_file):  # if object is folder go inside and start self
                os.chdir(dir_file)
                sub_start = list(Path(dir_file).iterdir())
                add_missed_items(sub_start)  # recursion
            else:
                destination_file = os.path.abspath(dir_file).replace(source_path, replica_path)
                destination_path = os.path.dirname(dir_file).replace(source_path, replica_path)
                test_dir_path(destination_path)  # if folder not exist will be created
                if not os.path.exists(destination_file):  # if file not exist will be copied
                    shutil.copy(os.path.abspath(dir_file), destination_path)
                    log_row("copy file", destination_file)
                source_file_hash = get_file_hash(dir_file)  # get hash 1
                replica_file_hash = get_file_hash(destination_file)  # get hash 2
                if source_file_hash != replica_file_hash:  # compare files
                    shutil.copy(os.path.abspath(dir_file), destination_path)
                    log_row("update file", destination_file)
    else:
        locality = os.getcwd()
        dest_locality = locality.replace(source_path, replica_path)
        test_dir_path(dest_locality)


# replica cleaning function (recursive)
def delete_items(curr_folder):
    if len(curr_folder) != 0:
        for dir_file in curr_folder:
            if os.path.isdir(dir_file):  # if object is folder go inside and start self
                os.chdir(dir_file)
                sub_start = list(Path(dir_file).iterdir())
                delete_items(sub_start)  # recursion
            else:
                destination_file = os.path.abspath(dir_file).replace(replica_path, source_path)
                test_dir_path(destination_file, delete=True)  # if file exist will be removed
    else:
        locality = os.getcwd()
        os.chdir('..')
        dest_locality = locality.replace(replica_path, source_path)
        test_dir_path(dest_locality, delete=True)


# function for getting hash
def get_file_hash(file_path):
    hash_object = hashlib.md5()  # md5 fast algorithm
    with open(file_path, 'rb') as file:
        for block in iter(lambda: file.read(4096), b''):
            hash_object.update(block)
    file_hash = hash_object.hexdigest()
    return file_hash

# spec symbols check function
def has_special_characters(string):
    if re.search(pattern, string):
        return True
    else:
        return False


# Start
source_path = ''
replica_path = ''
log_path = ''
pattern = r'[-=+~;#$%^&()@!<>"|?*\x00-\x1F]'

inp_pth = True
while inp_pth:
    source_path = input("Enter the source path: ")
    if has_special_characters(source_path):
        print("special symbols not allowed in path")
    elif not os.path.exists(source_path):
        print("this folder not exist")
    else:
        print("ok")
        inp_pth = False

inp_pth = True
while inp_pth:
    replica_path = input("Enter the replica path: ")
    if has_special_characters(replica_path):
        print("special symbols not allowed in path")
    elif replica_path.lower() == source_path.lower():
        print("path for replica match with source")
    else:
        print("ok")
        inp_pth = False

sync_interval_sec = int(input("Enter the sync interval in seconds: "))

inp_pth = True
while inp_pth:
    log_path = input("Enter the path to log file: ")
    if has_special_characters(log_path):
        print("special symbols not allowed in path")
    elif log_path.lower() == source_path.lower():
        print("path for log file match with source")
    elif log_path.lower() == replica_path.lower():
        print("path for log file match with replica")
    else:
        print("ok")
        inp_pth = False

"""
# debug mode
source_path = os.path.join("C:\\TEMP\\veeam\\source")
replica_path = os.path.join("C:\\TEMP\\veeam\\replica")
sync_interval_sec = 5
log_path = os.path.join("C:\\TEMP\\veeam")
"""

# Check if the replica exists (and create if not)
test_dir_path(replica_path)

# (optional)
# delete old log-file before run
if os.path.exists(os.path.join(log_path, "SyncVeeam.log")):
    os.remove(os.path.join(log_path, "SyncVeeam.log"))

# Run main cycle
log_row("sync start", "*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*")

while True:
    start_point_source = list(Path(source_path).iterdir())
    add_missed_items(start_point_source)
    start_point_replica = list(Path(replica_path).iterdir())
    delete_items(start_point_replica)
    time.sleep(sync_interval_sec)
