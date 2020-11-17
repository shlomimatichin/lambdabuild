#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
# pylint: disable=C0103
import argparse
import os
import shutil
import re
import argcomplete
from lambdabuild import dockerwrapper
from lambdabuild import dockerfiletemplates
from lambdabuild import runtimeinfo
from lambdabuild import byteequivalentzip
from lambdabuild import untar
from lambdabuild import collectsources

parser = argparse.ArgumentParser()
parser.add_argument("--runtime", default="3.6")
parser.add_argument(
    "--base-docker",
    choices=[
        "lambci/lambda:build-python3.8",
        "lambci/lambda:build-python3.7",
        "lambci/lambda:build-python3.6",
        "lambci/lambda:build-python3.7",
        "lambci/lambda:build-python2.7",
        "amazonlinux:2017.03",
    ])
parser.add_argument("--output-zip", required=True)
parser.add_argument(
    "--source-code-root-dirs", default=[], nargs="+",
    help="each argument is a directory to copy whole contents to the task root")
parser.add_argument(
    "--source-code-dirs", default=[], nargs="+",
    help="each argument is a directory to copy to the task root, keeping the basename")
parser.add_argument(
    "--source-code-relative", default=[], nargs="+",
    help="each argument is a colon separated pair: <directory to copy relativly from>:<target in artifact>")
parser.add_argument(
    "--source-code-renamed", default=[], nargs="+",
    help="each argument is a colon separated pair: <source file or directory to copy>:<target in artifact>")
parser.add_argument(
    "--raw-files-root-dirs", default=[], nargs="+",
    help="each argument is a directory to copy whole contents to the task root "
    "(files are not removed by entry-point optimization)")
parser.add_argument(
    "--raw-files-dirs", default=[], nargs="+",
    help="each argument is a directory to copy to the task root, keeping the basename "
    "(files are not removed by entry-point optimization)")
parser.add_argument(
    "--raw-files-relative", default=[], nargs="+",
    help="each argument is a colon separated pair: <directory to copy relativly from>:<target in artifact>"
    "(files are not removed by entry-point optimization)")
parser.add_argument(
    "--raw-files-renamed", default=[], nargs="+",
    help="each argument is a colon separated pair: <source file or directory to copy>:<target in artifact> "
    "(files are not removed by entry-point optimization)")
parser.add_argument("--exclude-dirs", nargs="+", default=["tests", "test"],
                    help="directory basenames to exclude from docker build context")
parser.add_argument("--exclude-basenames", nargs="+", default=[".gitignore", "tags"],
                    help="file basenames to exclude from docker build context")
parser.add_argument("--exclude-regexes", nargs="+", default=[],
                    help="full path regexes to exclude from docker build context")

subparsers = parser.add_subparsers(dest="cmd")
artifact_cmd = subparsers.add_parser(
    "artifact",
    help="compile your code into an artifact")
artifact_cmd.add_argument(
    "--entry-points",
    required=True,
    nargs="+",
    help="absolute python module path to find minimal modules set from. "
    "specify an empty argument to disable this feature")

layer_cmd = subparsers.add_parser(
    "layer",
    help="build layer from python dependencies")
input_group = layer_cmd.add_mutually_exclusive_group(required=True)
input_group.add_argument("--requirements", help="requirements in command line")
input_group.add_argument("--requirements-file", help="requirements.txt file")
layer_cmd.add_argument("--keep-sources", action="store_true", help="keep .py files")

custom_cmd = subparsers.add_parser(
    "custom",
    help="build byte equivilent zip from a tar created by a dockerfile. make "
    "sure to put file in /custom.tar in provided dockerfile.")
custom_cmd.add_argument("--dockerfile", required=True)

argcomplete.autocomplete(parser)
args = parser.parse_args()


def create_build_dir():
    build_dir = args.output_zip + ".build"
    if os.path.isdir(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)
    shutil.copy(os.path.join(os.path.dirname(__file__), "clean_lambda_directory_before_zip_python2.py"), build_dir)
    shutil.copy(os.path.join(os.path.dirname(__file__), "clean_lambda_directory_before_zip_python3.py"), build_dir)
    return build_dir


def delete_excluded_files(build_dir):
    regexes = [re.compile(r) for r in args.exclude_regexes]
    for root, dirs, files in os.walk(build_dir):
        for dirname in args.exclude_dirs:
            if dirname in dirs:
                dirs.remove(dirname)
                shutil.rmtree(os.path.join(root, dirname))
        for basename in args.exclude_basenames:
            if basename in files:
                files.remove(basename)
                os.unlink(os.path.join(root, basename))
        for basename in files:
            fullpath = os.path.join(root, basename)
            for regex in regexes:
                if regex.search(fullpath):
                    os.unlink(fullpath)
                    break


def build_and_zip(build_dir, tar_filename):
    output_tar = dockerwrapper.build_and_extract_file(build_dir, tar_filename)
    with byteequivalentzip.createzip(args.output_zip) as add_to_zip:
        for name, contents in untar.unpack_in_memory_tar(output_tar, sort=True):
            add_to_zip(name, contents)


build_dir = create_build_dir()
collectsources.collect_sources(destination=os.path.join(build_dir, "sourcecode"),
                               root_dirs=args.source_code_root_dirs,
                               dirs=args.source_code_dirs,
                               relative=args.source_code_relative,
                               renamed=args.source_code_renamed)
collectsources.collect_sources(destination=os.path.join(build_dir, "rawfiles"),
                               root_dirs=args.raw_files_root_dirs,
                               dirs=args.raw_files_dirs,
                               relative=args.raw_files_relative,
                               renamed=args.raw_files_renamed)
delete_excluded_files(build_dir)

if args.cmd == "artifact":
    entry_points = ""
    if args.entry_points != [""]:
        entry_points = "--entry-points " + " ".join(args.entry_points)
    with open(f"{build_dir}/Dockerfile", "w") as writer:
        writer.write(dockerfiletemplates.BUILD_ARTIFACT % dict(
            runtimeinfo.RUNTIMES[args.runtime],
            entry_points=entry_points))
    build_and_zip(build_dir, "/artifact.tar")
elif args.cmd == "layer":
    if args.requirements is not None:
        requirements = args.requirements
    else:
        with open(args.requirements_file) as reader:
            requirements = reader.read().replace("\n", " ")
    sourceless = not args.keep_sources
    with open(f"{build_dir}/Dockerfile", "w") as writer:
        writer.write(dockerfiletemplates.BUILD_LAYER % dict(
            runtimeinfo.RUNTIMES[args.runtime],
            requirements=requirements,
            sourceless="--sourceless" if sourceless else ""))
    build_and_zip(build_dir, "/layer.tar")
elif args.cmd == "custom":
    shutil.copy(args.dockerfile, f"{build_dir}/Dockerfile")
    build_and_zip(build_dir, "/custom.tar")
else:
    raise AssertionError("Unknown command: %s" % args.cmd)


def _main():
    pass
