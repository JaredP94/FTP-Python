# Authored by Jared Ping

import grp
import pwd
import time
import os
import stat

def fileProperty(filepath):
    # Returns information from given file, i.e: "-rw-r--r-- 1 User Group 312 Feb 27 2018 filename"
    filepath_stat = os.stat(filepath)
    file_info = []

    def getFileMode():
        modes = [
            stat.S_IRUSR, stat.S_IWUSR, stat.S_IXUSR,
            stat.S_IRGRP, stat.S_IWGRP, stat.S_IXGRP,
            stat.S_IROTH, stat.S_IWOTH, stat.S_IXOTH,
        ]
        mode     = filepath_stat.st_mode
        fullmode = ''
        fullmode += os.path.isdir(filepath) and 'd' or '-'

        for index in range(9):
            fullmode += bool(mode & modes[index]) and 'rwxrwxrwx'[index] or '-'

        return fullmode

    def getFilesNumber():
        # Number of hard links
        return str(filepath_stat.st_nlink)

    def getUser():
        # File owner
        return pwd.getpwuid(filepath_stat.st_uid).pw_name

    def getGroup():
        # File group association
        return grp.getgrgid(filepath_stat.st_gid).gr_name

    def getSize():
        # Size of file in bytes
        return str(filepath_stat.st_size)

    def getLastTime():
        # Time of most recent content modification
        return time.strftime('%b %d %H:%M', time.gmtime(filepath_stat.st_mtime))

    for function in ('getFileMode()', 'getFilesNumber()', 'getUser()', 'getGroup()', 'getSize()', 'getLastTime()'):
        file_info.append(eval(function))

    file_info.append(os.path.basename(filepath))
    return ' '.join(file_info)
