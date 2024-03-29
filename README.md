crcmanip ![build](https://github.com/rr-/pycrcmanip/workflows/build/badge.svg) [![codecov](https://codecov.io/gh/rr-/pycrcmanip/branch/master/graph/badge.svg?token=S50CNBHNLZ)](https://codecov.io/gh/rr-/pycrcmanip)
========

A command line interface tool that lets you reverse and freely change CRC
checksums through smart file patching.

It's a successor to [my previous C++
variant](https://github.com/rr-/CRC-manipulator) of this project. Even though
this version is written in Python, the performance is comparable to the old C++
version.

### Features

Patching and calculating CRC checksums for:

- CRC32
- CRC32POSIX (`cksum` from GNU coreutils)
- CRC16CCITT
- CRC16IBM
- CRC16XMODEM

### How it works

It appends a few bytes at the end of the file so that the file checksum
computes to a given hexadecimal hash.

### Example

```console
$ echo -n hello > test.txt
$ crc32 test.txt
3610a686
$ crcmanip calc test.txt
3610A686
$ crcmanip patch test.txt deadbeef
$ crcmanip calc test.txt
DEADBEEF
$ crc32 test.txt
deadbeef
$ cat test.txt
helloE~40
```

### Installing

To install the newest version from GitHub:

```
$ git clone https://github.com/rr-/pycrcmanip.git
$ cd pycrcmanip
$ pip install --user .
$ crcmanip --help
```

### Testing

```
$ pytest
```

### Contributing

To set up the project:
```sh
pip install --user poetry poethepoet

git clone https://github.com/rr-/pycrcmanip.git
cd pycrcmanip

poetry install
poetry run pre-commit install
```

To run tests:
```
poe test
```

To run the profiler:
```
poe profile
```

To clean build artifacts:
```
poe clean
```
