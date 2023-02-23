#!/usr/bin/env python3
import random

import atheris
import sys
import io
import fuzz_helpers
import random
from contextlib import contextmanager

with atheris.instrument_imports(include=['pymzml', 'xml']):
    import pymzml

# Exceptions
from xml.etree.ElementTree import ParseError
from gzip import BadGzipFile
from zlib import error


@contextmanager
def nostdout():
    save_stdout = sys.stdout
    save_stderr = sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    yield
    sys.stdout = save_stdout
    sys.stderr = save_stderr


def TestOneInput(data):
    fdp = fuzz_helpers.EnhancedFuzzedDataProvider(data)
    try:
        with fdp.ConsumeTemporaryFile('.chrm.mzML.gz', all_data=True) as f, nostdout():
            pymzml.run.Reader(f)
    except (ParseError, BadGzipFile, UnicodeDecodeError, error, EOFError):
        return -1
    except LookupError as e:
        if random.random() > 0.90:
            raise e
        return 0
    except Exception as e:
        if 'not a gzip' in str(e):
            return -1
        raise e


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
