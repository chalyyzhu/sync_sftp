from stat import S_ISDIR, S_ISREG
from datetime import datetime
import pytz
import pysftp
import os, json , time
import threading
import shutil

"' SFTP AUTOMATIC SYNCRONIZE '"
tz = pytz.timezone("Asia/Jakarta")



class SFTPAutoSync:
    
    def __init__(self, host, username, password, filters=[]):
       self.sftp = pysftp.Connection(host, username, password=password)
       self.data = {}
       self.data_local = {}
       self.filters = filters

    def sync_d(self, ftp_path, locale_path):
        for fname in os.listdir(locale_path):
            Fpath = os.path.join(locale_path, fname)
            Rpath = os.path.join(ftp_path, fname)
            attr = os.stat(Fpath)
            self.data_local[Rpath] = attr.st_mtime
            if S_ISDIR(attr.st_mode):
                if fname not in self.filters:
                   self.sync_d(Rpath, Fpath)
            elif S_ISREG(attr.st_mode):
                
                if Rpath in self.data:
                  if attr.st_mtime > self.data[Rpath]:
                      now = datetime.now(tz=tz).strftime('%d/%m/%Y | %H:%M ')
                      print(now +" => Uploading ....  : "+Rpath)
                      self.sftp.put(Fpath, Rpath, preserve_mtime = False)
                else:
                    now = datetime.now(tz=tz).strftime('%d/%m/%Y | %H:%M ')
                    print(now+" => Uploading ....  : "+Rpath)
                    self.sftp.put(Fpath, Rpath, preserve_mtime = False)

                                     
    def sync(self, remotedir, localdir):
        for item in self.sftp.listdir_attr(remotedir):
            remote_dir_item = os.path.join(remotedir, item.filename)
            locale_dir_item = os.path.join(localdir, item.filename)
            self.data[remote_dir_item] = item.st_mtime
            if S_ISDIR(item.st_mode):
                try: os.makedirs(locale_dir_item)
                except: pass
                if  item.filename not in self.filters:
                    self.sync(remote_dir_item, locale_dir_item)
            elif S_ISREG(item.st_mode):
                
                if (not os.path.isfile(locale_dir_item) or (item.st_mtime > os.path.getmtime(locale_dir_item))):
                   now = datetime.now(tz=tz).strftime('%d/%m/%Y | %H:%M ')
                   print(now+" => Downloadin %s..." % remote_dir_item)
                   self.sftp.get(remote_dir_item, locale_dir_item, preserve_mtime = True)

    def find_data(self, dict, find):
        for item in dict:
            if find in item:
                return True
        return False
        

    def ftp_find_del(self, local_dir):
        items_removed = 0
        for item in os.listdir(local_dir):
            local_dir_item = os.path.join(local_dir, item)
            if not self.find_data(self.data, item):
                now = datetime.now(tz=tz).strftime('%d/%m/%Y | %H:%M ')
                print(now+' => removing {}'.format(local_dir_item))
                self._remove(local_dir_item)
                items_removed += 1
            else:
                if os.path.isdir(local_dir_item):
                    items_removed += self.ftp_find_del(local_dir_item)
        return items_removed
    
    def _remove(self, path):
        try:
            if os.path.isfile(path):
                os.remove(path)  # remove file
            else:
                shutil.rmtree(path)  # remove directory
        except Exception as e:
            now = datetime.now(tz=tz).strftime('%d/%m/%Y | %H:%M ')
            print(now+" => could not remove {}, error {0}".format(path, str(e)))

    def normalize(self):
        self.data = {}
        self.data_local = {}
