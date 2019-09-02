#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface for indexed gzipped files

@author: Manuel Koesters
"""

# Python mzML module - pymzml
# Copyright (C) 2010-2019 M. Kösters, C. Fufezan
#     The MIT License (MIT)

#     Permission is hereby granted, free of charge, to any person obtaining a copy
#     of this software and associated documentation files (the "Software"), to deal
#     in the Software without restriction, including without limitation the rights
#     to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#     copies of the Software, and to permit persons to whom the Software is
#     furnished to do so, subject to the following conditions:

#     The above copyright notice and this permission notice shall be included in all
#     copies or substantial portions of the Software.

#     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#     IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#     FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#     AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#     LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#     OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#     SOFTWARE.

import codecs
import gzip
from xml.etree.ElementTree import XML

from .. import spec
from ..utils.GSGR import GSGR


class IndexedGzip:
    def __init__(self, path, encoding):
        """
        Initialize Wrapper object for indexed gzipped files.

        Arguments:
            path (str)     : path to the file
            encoding (str) : encoding of the file
        """
        self.path = path
        self.file_handler = codecs.getreader(encoding)(gzip.open(path))
        self.offset_dict = dict()
        self._build_index()

    def __del__(self):
        """Close handlers when deleting object."""
        self.Reader.close()
        self.file_handler.close()

    def _build_index(self):
        """Use the GSGR class to retrieve the index from the file and save it."""
        self.Reader = GSGR(self.path)
        self.offset_dict = self.Reader.index

    def read(self, size=-1):
        """
        Read binary data from file handler.

        Keyword Arguments:
            size (int): Number of bytes to read from file, -1 to read to end of file

        Returns:
            data (str): byte string of len size of input data
        """
        return self.file_handler.read(size)

    def __getitem__(self, identifier):
        """
        Access the item with id 'identifier' in the file.

        Arguments:
            identifier (str): native id of the item to access

        Returns:
            data (str): text associated with the given identifier
        """

        # TODO more elegant way to add NameSpace (.register_namespace maybe??)
        ns_prefix = '<mzML xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://psi.hupo.org/ms/mzml http://psidev.info/files/ms/mzML/xsd/mzML1.1.0.xsd" id="test_Creinhardtii_QE_pH8" version="1.1.0" xmlns="http://psi.hupo.org/ms/mzml">'
        ns_suffix = "</mzML>"
        data = self.Reader.read_block(identifier)
        element = XML(ns_prefix + data.decode("utf-8") + ns_suffix)
        if "chromatogram" in element[0].tag:
            return spec.Chromatogram(list(element)[0], measured_precision=5e-6)
        else:
            return spec.Spectrum(list(element)[0], measured_precision=5e-6)

    def close(self):
        """Close the handlers."""
        self.Reader.close()
        self.file_handler.close()


if __name__ == "__main__":
    print(__doc__)
