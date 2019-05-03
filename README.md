# LambdaBuild

This is a single command line executable meant to be triggerred from within
make or make like script, which automates creation of AWS lambda python artifacts,
and AWS lambda layers.

### Features:
* build inside docker emulating lambda environment, with target python runtime
* precompile .pyc files, for faster cold starts
* support build-only-if-changed
* result zip file hash will remain identical between builds (important when
  infrastructure as code decides wether to update lambda / layer, since
  previous build was not on same machine)
