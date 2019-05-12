import os
import shutil
import distutils.dir_util


def collect_sources(destination, root_dirs, dirs, relative, renamed):
    os.makedirs(destination)
    for source in root_dirs:
        _copy(source, destination)
    for source in dirs:
        _copy(source, _rebase(source, destination))
    for pair in relative:
        source, relative_target = pair.split(":")
        _copy(os.path.join(source, relative_target), os.path.join(destination, relative_target))
    for pair in renamed:
        source, target = pair.split(":")
        _copy(source, os.path.join(destination, target))


def _copy(source, destination):
    if os.path.isdir(source):
        distutils.dir_util.copy_tree(source, destination, preserve_symlinks=1)
    else:
        if not os.path.isdir(os.path.dirname(destination)):
            os.makedirs(os.path.dirname(destination))
        shutil.copy(source, destination)


def _rebase(source, destination):
    return os.path.join(destination, os.path.basename(source))
