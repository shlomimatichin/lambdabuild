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
artifact_cmd.add_argument(
    "--entry-points",
    required=True,
    nargs="+",
    help="absolute python module path to find minimal modules set from. "
    "specify an empty argument to disable this feature")
artifact_cmd.add_argument(
    "--source-code-root-dirs", default=[], nargs="+",
    help="each argument is a directory to copy whole contents to the task root")
artifact_cmd.add_argument(
    "--source-code-dirs", default=[], nargs="+",
    help="each argument is a directory to copy to the task root, keeping the basename")
artifact_cmd.add_argument(
    "--source-code-relative", default=[], nargs="+",
    help="each argument is a colon separated pair: <directory to copy relativly from>:<target in artifact>")
artifact_cmd.add_argument(
    "--source-code-renamed", default=[], nargs="+",
    help="each argument is a colon separated pair: <source file or directory to copy>:<target in artifact>")
artifact_cmd.add_argument(
    "--raw-files-root-dirs", default=[], nargs="+",
    help="each argument is a directory to copy whole contents to the task root "
    "(files are not removed by entry-point optimization)")
artifact_cmd.add_argument(
    "--raw-files-dirs", default=[], nargs="+",
    help="each argument is a directory to copy to the task root, keeping the basename "
    "(files are not removed by entry-point optimization)")
artifact_cmd.add_argument(
    "--raw-files-relative", default=[], nargs="+",
    help="each argument is a colon separated pair: <directory to copy relativly from>:<target in artifact>"
    "(files are not removed by entry-point optimization)")
artifact_cmd.add_argument(
    "--raw-files-renamed", default=[], nargs="+",
    help="each argument is a colon separated pair: <source file or directory to copy>:<target in artifact> "
    "(files are not removed by entry-point optimization)")
artifact_cmd.add_argument("--exclude-dirs", nargs="+", default=[])
artifact_cmd.add_argument("--exclude-basenames", nargs="+", default=[".gitignore"])
artifact_cmd.add_argument("--exclude-regexes", nargs="+", default=[])
layer_cmd = subparsers.add_parser(
    "layer",
    help="build layer from python dependencies")
layer_cmd.add_argument("--output-zip", required=True)
input_group = layer_cmd.add_mutually_exclusive_group(required=True)
input_group.add_argument("--requirements")
input_group.add_argument("--requirements-file")

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


if args.cmd == "artifact":
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
    entry_points = ""
    if args.entry_points != [""]:
        entry_points = "--entry-points " + " ".join(args.entry_points)
    with open(f"{build_dir}/Dockerfile", "w") as writer:
        writer.write(dockerfiletemplates.BUILD_ARTIFACT % dict(
            runtimeinfo.RUNTIMES[args.runtime],
            entry_points=entry_points))
    artifact_tar = dockerwrapper.build_and_extract_file(build_dir, "/artifact.tar")
    with byteequivalentzip.createzip(args.output_zip) as add_to_zip:
        for name, contents in untar.unpack_in_memory_tar(artifact_tar):
            add_to_zip(name, contents)
elif args.cmd == "layer":
    build_dir = create_build_dir()
    if args.requirements:
        requirements = args.requirements
    else:
        with open(args.requirements_file) as reader:
            requirements = reader.read().replace("\n", " ")
    with open(f"{build_dir}/Dockerfile", "w") as writer:
        writer.write(dockerfiletemplates.BUILD_LAYER % dict(
            runtimeinfo.RUNTIMES[args.runtime],
            requirements=requirements))
    layer_tar = dockerwrapper.build_and_extract_file(build_dir, "/layer.tar")
    with byteequivalentzip.createzip(args.output_zip) as add_to_zip:
        for name, contents in untar.unpack_in_memory_tar(layer_tar):
            add_to_zip(name, contents)
else:
    raise AssertionError("Unknown command: %s" % args.cmd)


def _main():
    pass
