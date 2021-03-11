#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2019--2021 Matt Post <post@cs.jhu.edu>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Script that takes one or more XML files of papers in the Anthology as 
arguments and does the following:

    -Finds all papers with one author and adds "Matt POST" as a coauthor
    -Finds all papers with more than two authors, and removes authors 3+
    -Transforms each author's last name to ALL CAPS

It then writes out the modified XML file(s).

Authors: Matt Post & Mourad Heddaya
"""

import argparse
import os
import re
import readline
import shutil
import sys

import lxml.etree as etree

from collections import defaultdict, OrderedDict
from datetime import datetime

from normalize_anth import normalize
from anthology.utils import (
    make_simple_element,
    build_anthology_id,
    deconstruct_anthology_id,
    indent,
    compute_hash_from_file,
)
from anthology.index import AnthologyIndex
from anthology.people import PersonName
from anthology.bibtex import read_bibtex
from anthology.venues import VenueIndex

from itertools import chain
from typing import Dict, Any

def main(args):
    for collection_file in args.files:
        root_node = etree.parse(collection_file).getroot()
        for paper in root_node.findall(".//paper"):
            authors = paper.findall("./author")
            n_authors = len(authors)
            for idx, author in enumerate(authors):
                if n_authors == 1:
                    # Create new XML author element for author Matt POST
                    new_author = make_simple_element("author", parent=paper)
                    make_simple_element("first", "Matt", parent=new_author)
                    make_simple_element("last", "POST", parent=new_author)
                    # Inserts new author "Matt POST" after current and only other author
                    paper.insert(paper.index(author)+1, new_author)
                elif idx > 1:
                    # Remove authors authors 3+ if there are more than 2 authors
                    paper.remove(author)
                    # Continue to avoid running unnecessary code below for authors 3+
                    continue
                # Transforms each author's last name to ALL CAPS
                last = author.find("./last")
                last.text = last.text.upper()

        tree = etree.ElementTree(root_node)
        indent(root_node)
        tree.write(
            collection_file, encoding="UTF-8", xml_declaration=True, with_tail=True
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", help="List of XML files.")
    args = parser.parse_args()
    main(args)
