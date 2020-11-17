import zipfile
import os
import time
import datetime
import struct
import contextlib

PYC_TIMESTAMP = datetime.date(1981, 1, 1)
PYC_UNIX_TIMESTAMP = struct.pack("I", int(time.mktime(PYC_TIMESTAMP.timetuple())))
PYTHON36_HEADER = b"\x33\x0d\x0d\x0a"
PYTHON37_HEADER = b"\x42\x0d\x0d\x0a"
PYTHON38_HEADER = b"\x55\x0d\x0d\x0a"
PYTHON27_HEADER = b"\x03\xf3\x0d\x0a"


@contextlib.contextmanager
def createzip(zipfile_path):
    context = dict(lastName=None)
    with zipfile.ZipFile(zipfile_path + ".tmp", "w", compression=zipfile.ZIP_DEFLATED) as zipper:
        def _add_to_zip(name, contents):
            if context['lastName'] is not None:
                assert name > context['lastName'], \
                    "Input filename must be alphabetically sorted to assure byte equivalancy: %s <= %s" % (
                        name, context['lastName'])
            context['lastName'] = name
            if name.endswith(".pyc"):
                assert len(PYC_UNIX_TIMESTAMP) == 4
                if contents.startswith(PYTHON37_HEADER) or contents.startswith(PYTHON38_HEADER):
                    contents = contents[:8] + PYC_UNIX_TIMESTAMP + contents[12:]
                else:
                    assert contents.startswith(PYTHON27_HEADER) or contents.startswith(PYTHON36_HEADER), \
                            "Unrecognized pyc header, are you using python 2.7, 3.6 or 3.7? %s" % contents[:4]
                    contents = contents[:4] + PYC_UNIX_TIMESTAMP + contents[8:]
            info = zipfile.ZipInfo(filename=name, date_time=(1980, 1, 1, 0, 0, 0))
            info.external_attr |= (0x1a4 << 16)
            zipper.writestr(info, contents, compress_type=zipfile.ZIP_DEFLATED)
        yield _add_to_zip
    os.rename(zipfile_path + ".tmp", zipfile_path)
