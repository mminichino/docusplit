#!/usr/bin/env python3

import argparse
import warnings
import logging
import os
from docusplit import DocuSplit

warnings.filterwarnings("ignore")
logger = logging.getLogger()


class Params(object):

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--file", action="store", help="Input File")
        parser.add_argument('--host', action='store', help="Hostname or IP address", default="127.0.0.1")
        parser.add_argument('--user', action='store', help="User Name", default="Administrator")
        parser.add_argument('--password', action='store', help="User Password", default="password")
        parser.add_argument('--bucket', action='store', help="Test Bucket", default="testrun")
        parser.add_argument("--scope", action="store", help="Scope")
        parser.add_argument("--collection", action="store", help="Collections")
        parser.add_argument("--dump", action="store_true", help="Dump to JSON")
        parser.add_argument("--flat", action="store_true", help="Dump to Flattened JSON")
        parser.add_argument("--split", action="store_true", help="Split Large File")
        parser.add_argument("--list", action="store_true", help="Split File Using List Object")
        parser.add_argument("--dir", action="store", help="Output Directory")
        parser.add_argument("--base", action="store", help="Output Filename Base")
        parser.add_argument("--key", action="store", help="Key to Extract and Remove")
        parser.add_argument("-v", "--verbose", action="store_true", help="Verbose")
        parser.add_argument("--depth", action="store", help="Start Depth", type=int, default=0)
        self.args = parser.parse_args()

    @property
    def parameters(self):
        return self.args


def manual_1(parameters):
    with open(parameters.file, mode="rb") as input_xml:
        contents = input_xml.read()
    if parameters.dump:
        if parameters.flat:
            d = DocuSplit(contents, parameters.depth)
            d.dump_flattened_json()
        elif parameters.split:
            if parameters.key:
                if parameters.list:
                    d = DocuSplit(contents, parameters.depth)
                    d.split_sub_doc_list(parameters.base, parameters.dir, parameters.key)
                else:
                    d = DocuSplit(contents, parameters.depth)
                    d.split_sub_doc(parameters.base, parameters.dir, parameters.key)
            else:
                d = DocuSplit(contents, parameters.depth)
                d.split_json(parameters.base, parameters.dir)
        else:
            d = DocuSplit(contents, parameters.depth)
            d.dump_to_json()
    else:
        d = DocuSplit(contents, parameters.depth)
        d.dump_stats(parameters.verbose)


p = Params()
options = p.parameters

try:
    debug_level = int(os.environ['DEBUG_LEVEL'])
except (ValueError, KeyError):
    debug_level = 3

if debug_level == 0:
    logger.setLevel(logging.DEBUG)
elif debug_level == 1:
    logger.setLevel(logging.ERROR)
elif debug_level == 2:
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.CRITICAL)

logging.basicConfig()

manual_1(options)
