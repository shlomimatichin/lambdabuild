#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
# pylint: disable=C0103
import argparse
import os
import shutil
import argcomplete
from lambdabuild import dockerwrapper
from lambdabuild import dockerfiletemplates
from lambdabuild import runtimeinfo

parser = argparse.ArgumentParser()
parser.add_argument("--runtime", default="3.6")
parser.add_argument(
    "--base-docker",
    choices=[
        "lambci/lambda:build-python3.6",
        "lambci/lambda:build-python3.7",
        "lambci/lambda:build-python2.7",
        "amazonlinux:2017.03",
    ])
subparsers = parser.add_subparsers(dest="cmd")
artifact_cmd = subparsers.add_parser(
    "artifact",
    help="compile your code into an artifact")
artifact_cmd.add_argument("--output-zip", required=True)
layer_cmd = subparsers.add_parser(
    "layer",
    help="build layer from python dependencies")
layer_cmd.add_argument("--output-zip", required=True)
input_group = layer_cmd.add_mutually_exclusive_group(required=True)
input_group.add_argument("--requirements")
input_group.add_argument("--requirements-file")
layer_cmd.add_argument("--build-dir")

argcomplete.autocomplete(parser)
args = parser.parse_args()

if args.cmd == "artifact":
    pass
elif args.cmd == "layer":
    build_dir = args.build_dir or args.output_zip + ".build"
    if os.path.isdir(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)
    if args.requirements:
        requirements = args.requirements
    else:
        with open(args.requirements_file) as reader:
            requirements = reader.read().replace("\n", " ")
    shutil.copy(os.path.join(os.path.dirname(__file__), "clean_lambda_directory_before_zip_python2.py"), build_dir)
    shutil.copy(os.path.join(os.path.dirname(__file__), "clean_lambda_directory_before_zip_python3.py"), build_dir)
    with open(f"{build_dir}/Dockerfile", "w") as writer:
        writer.write(dockerfiletemplates.BUILD_LAYER % dict(
            runtimeinfo.RUNTIMES[args.runtime],
            requirements=requirements))
    image_id = dockerwrapper.build(build_dir)
    dockerwrapper.extract_file_from_image(image_id, "/layer.zip", args.output_zip)
else:
    raise AssertionError("Unknown command: %s" % args.cmd)


def _main():
    pass
