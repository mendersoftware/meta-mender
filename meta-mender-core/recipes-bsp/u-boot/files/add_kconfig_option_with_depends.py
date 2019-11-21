#/usr/bin/python3

# Convenience script to add a Kconfig option, and at the same time add the
# "depends on" entries for that option. This is hard to do in shell.

import argparse
import os
import re

parser = argparse.ArgumentParser()
parser.add_argument("--src-dir", required=True,
                    help="Directory containing sources.")
parser.add_argument("--defconfig-file", required=True,
                    help="The file containing defconfig entries.")
parser.add_argument("option", metavar="OPTION", nargs=1,
                    help="Option to add to Kconfig, expressed as KEY=VALUE.")
args = parser.parse_args()

def parse_dependencies(depends_string):
    # if depends_string has multiple alternative dependencies ("A || B"),
    # select the first one ("A")
    depends_string = re.split("\s*\|\|\s*", depends_string)[0]

    # if there are parentheses around ("(A && B)"), remove them ("A && B")
    match = re.match("^\(\s*(.*)\s*\)$", depends_string)
    if match:
        depends_string = match[1]

    # if depends_string has multiple required dependencies ("A && B"),
    # return all of them
    dependencies = re.split("\s*&&\s*", depends_string)

    return dependencies

def add_kconfig_option(option):
    key, value = option.split("=", 1)

    with open(args.defconfig_file) as fd:
        if any([line.startswith("%s=" % key) for line in fd.readlines()]):
            # Already added, skip.
            return

    for dirpath, dirnames, filenames in os.walk(args.src_dir):
        for filename in filenames:
            if filename != "Kconfig":
                continue
            with open(os.path.join(dirpath, filename)) as fd:
                if not key.startswith("CONFIG_"):
                    raise Exception("Not sure how to handle Kconfig option that doesn't start with 'CONFIG_'")
                kconfig_key = key[len("CONFIG_"):]
                inside_option = False
                for line in fd.readlines():
                    if re.match("^config\s*%s(\s|$)" % kconfig_key, line):
                        inside_option = True
                        continue
                    elif re.match("^config ", line):
                        inside_option = False
                        continue

                    if not inside_option:
                        continue

                    match = re.match("^\s*depends\s*on\s*(.+)", line)
                    if not match:
                        continue
                    for dependee in parse_dependencies(match.group(1)):
                        if dependee.startswith("!"):
                            # We're not handling negative dependencies right now.
                            continue
                        add_kconfig_option("CONFIG_%s=y" % dependee)

    with open(args.defconfig_file, "a") as fd:
        fd.write("%s\n" % option)

add_kconfig_option(args.option[0])
