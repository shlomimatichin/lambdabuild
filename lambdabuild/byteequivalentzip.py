import tarfile
import zipfile
import io
import os
import time
import datetime
import struct

PYC_TIMESTAMP = datetime.date(1981, 1, 1)
PYC_UNIX_TIMESTAMP = struct.pack("I", int(time.mktime(PYC_TIMESTAMP.timetuple())))


def unpack_tar_to_zipfile(tarfile_content, zipfile_path):
    tar = tarfile.open(mode="r", fileobj=io.BytesIO(tarfile_content))
    with zipfile.ZipFile(zipfile_path + ".tmp", "w", compression=zipfile.ZIP_DEFLATED) as zipper:
        for member in tar.getmembers():
            if member.type != tarfile.REGTYPE:
                continue
            contents = tar.extractfile(member).read()
            if member.name.endswith(".pyc"):
                assert len(PYC_UNIX_TIMESTAMP) == 4
                contents = contents[:4] + PYC_UNIX_TIMESTAMP + contents[8:]
            info = zipfile.ZipInfo(filename=member.name, date_time=(1980, 1, 1, 0, 0, 0))
            zipper.writestr(info, contents, compress_type=zipfile.ZIP_DEFLATED)
    os.rename(zipfile_path + ".tmp", zipfile_path)


def extract_tar_member(tarfile_content, name):
    tar = tarfile.open(mode="r", fileobj=io.BytesIO(tarfile_content))
    return tar.extractfile(name).read()
