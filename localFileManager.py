#!/usr/bin/env python
import re
import os
import urlparse
import uuid


def removeTempSuffix(filename):
    # type: (string)
    """removes '.tmp' from a filename string
    """
    assert filename.endswith(".tmp")
    return re.sub('\.tmp$', '', filename)


class LocalFileManager(object):
    """Gets all the files in 'fileIds_to_get' from the global fileStore
    and puts them in the local working directory. 
    returns: file_dict<file_id, (full_path, unique_file_name)>, work_dir
    """
    def __init__(self, job, fileIds_to_get, userFileNames=None):
        # type: (toil.job.Job, list<str>, dict<str, str>)
        self.owner_job = job
        self.work_dir  = os.path.dirname(os.path.realpath(__file__))
        self.file_dict = self._initialize_file_dict(fileIds_to_get, userFileNames)

    def localFileName(self, fileId):
        return self.file_dict[fileId][1]

    def localFilePath(self, fileId):
        return self.file_dict[fileId][0]

    def workDir(self):
        return self.work_dir + "/"

    @staticmethod
    def safeLocalDelete(local_file_list):
        removed_bools = []
        paths = [urlparse.urlparse(f).path for f in local_file_list]
        for url in paths:
            assert os.path.exists(url), "Didn'``t find {}".format(url)
            os.remove(url)
            removed_bools.append(not os.path.exists(url))
        return removed_bools

    def _initialize_file_dict(self, file_ids, userFileNames):
        file_dict = {}
        for f in file_ids:
            file_dict[f] = ""

        for file_id in file_dict.keys():
            self.owner_job.fileStore.logToMaster("preparing {}".format(file_id))
            if userFileNames is None:
                temp_file_name = uuid.uuid4().hex + ".tmp"
            else:
                assert file_id in userFileNames.keys(), \
                    "Didn't find user-specified path for {}".format(file_id)
                temp_file_name = userFileNames[file_id]
            destination_path = self.work_dir + "/{fn}".format(fn=temp_file_name)
            self.owner_job.fileStore.readGlobalFile(file_id, userPath=destination_path)
            assert(os.path.exists(destination_path)), "[]"
            file_dict[file_id] = (destination_path, temp_file_name)
        
        return file_dict
