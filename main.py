
import os, json,time
from sftp_sync.helper import SFTPAutoSync


host = "your_ip"
user_name = "root"
password = "xxxxx"

#change filters for not syncronize
filters = ['__pycache__', 'node_modules', '.','.git','tmp']

remote_path = "newjs"

main_path = os.path.join("backup", remote_path)
if not os.path.exists(main_path):os.makedirs(main_path)

sftp = SFTPAutoSync(host, user_name, password, filters)
print("[ FTP SYNC RUNNING... ]")
print("[ SYNCRONIZE FROM : {}/{}/{} ]".format(host, user_name,remote_path))
print("[ TO : {}]".format(main_path))


while True:
    try:
        
        print("...........................")
        sftp.normalize()         #refresh data
        sftp.sync(remote_path, main_path) #detect from sftp
        sftp.ftp_find_del(main_path)      #detect file deleted from sftp
        sftp.sync_d(remote_path, main_path) #detect localpath

    except Exception as e:
        print(e)
