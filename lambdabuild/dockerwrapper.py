import subprocess
import os
import tempfile
import tarfile
import io


def build(context_dir):
    with tempfile.TemporaryDirectory() as temp:
        iid_file = os.path.join(temp, "iid")
        subprocess.check_call(["docker", "build", context_dir, "--iidfile", iid_file])
        with open(iid_file) as reader:
            return reader.read().split(":")[1]


def extract_file_from_image_in_a_tar(image, source):
    container_id = subprocess.check_output(['docker', 'create', image]).decode().strip()
    try:
        return subprocess.check_output(['docker', 'cp', container_id + ":" + source, '-'])
    finally:
        subprocess.call(['docker', 'rm', '-v', container_id])


def build_and_extract_file(context_dir, source):
    image_id = build(context_dir)
    tar_with_one_file = extract_file_from_image_in_a_tar(image_id, source)
    tar = tarfile.open(mode="r", fileobj=io.BytesIO(tar_with_one_file))
    return tar.extractfile(source.lstrip('/')).read()
