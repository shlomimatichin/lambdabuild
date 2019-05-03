import subprocess
import os
import tempfile


def build(context_dir):
    with tempfile.TemporaryDirectory() as temp:
        iid_file = os.path.join(temp, "iid")
        subprocess.check_call(["docker", "build", context_dir, "--iidfile", iid_file])
        with open(iid_file) as reader:
            return reader.read().split(":")[1]


def extract_file_from_image(image, source, target):
    container_id = subprocess.check_output(['docker', 'create', image]).decode().strip()
    try:
        contents = subprocess.check_output(['docker', 'cp', container_id + ":" + source, '-'])
    finally:
        subprocess.call(['docker', 'rm', '-v', container_id])
    with open(target, "wb") as writer:
        writer.write(contents)
