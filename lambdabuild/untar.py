import tarfile
import io


def unpack_in_memory_tar(tarfile_content):
    tar = tarfile.open(mode="r", fileobj=io.BytesIO(tarfile_content))
    for member in tar.getmembers():
        if member.type != tarfile.REGTYPE:
            continue
        yield member.name, tar.extractfile(member).read()
