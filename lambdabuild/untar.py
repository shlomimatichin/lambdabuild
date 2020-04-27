import tarfile
import io


def unpack_in_memory_tar(tarfile_content, sort=False):
    tar = tarfile.open(mode="r", fileobj=io.BytesIO(tarfile_content))
    members = tar.getmembers()
    if sort:
        members = sorted(members, key=lambda m: m.name)
    for member in members:
        if member.type != tarfile.REGTYPE:
            continue
        yield member.name, tar.extractfile(member).read()
