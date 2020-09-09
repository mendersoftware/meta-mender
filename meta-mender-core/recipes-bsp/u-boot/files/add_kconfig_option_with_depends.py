#/usr/bin/python3

# Convenience script to add a Kconfig option, and at the same time add the
# "depends on" entries for that option. This is hard to do in shell.

import argparse
import os
import re
import boolean

parser = argparse.ArgumentParser()
parser.add_argument("--src-dir", required=True,
                    help="Directory containing sources.")
parser.add_argument("--defconfig-file", required=True,
                    help="The file containing defconfig entries.")
parser.add_argument("option", metavar="OPTION", nargs=1,
                    help="Option to add to Kconfig, expressed as KEY=VALUE.")
args = parser.parse_args()

def term_parse(term_string):
    term_string = term_string.replace("||","OR")
    term_string = term_string.replace("&&","AND")
    algebra = boolean.BooleanAlgebra()
    return algebra.parse(term_string)

def term_reduce_to_one_alternative(term, removal_terms):
    if type(term) == boolean.Symbol:
        if removal_terms.get(str(term)):
            # "Remove" term by returning None.
            return None
        else:
            # return symbol as is
            return term
    elif type(term) == boolean.NOT:
        # return Nonetype (do not handle negated terms)
        return None
    elif type(term) == boolean.OR:
        # Return None symbol if there is one, otherwise first alternative.
        # A bit counter-intuitive, ending at 0 omits the final 0 when counting
        # backwards.
        for term_pos in range(len(term.args)-1, 0, -1):
            result = term_reduce_to_one_alternative(term.args[term_pos], removal_terms)
            if result is None:
                return result
        return term_reduce_to_one_alternative(term.args[0], removal_terms)
    elif type(term) == boolean.AND:
        newterm = ()
        for subterm in term.args:
            newsubterm = term_reduce_to_one_alternative(subterm, removal_terms)
            if newsubterm != None:
                newterm += (newsubterm, )
        if len(newterm) == 0:
            return None
        elif len(newterm) == 1:
            return newterm[0]
        else:
            return boolean.AND(*newterm)
    else:
        raise ValueError

def term_to_string_list(term):
    items = []
    if type(term) == boolean.Symbol:
        items.append(str(term))
    elif type(term) == boolean.AND:
        for arg in term.args:
            items.append(str(arg))
    return items

def parse_dependencies(depends_string, already_added):
    depends_orig = term_parse(depends_string)
    depends_reduced = term_reduce_to_one_alternative(depends_orig, already_added)
    return term_to_string_list(depends_reduced)

def add_kconfig_option(option, already_added):
    key, value = option.split("=", 1)

    for dirpath, dirnames, filenames in os.walk(args.src_dir):
        for filename in filenames:
            if filename != "Kconfig":
                continue
            with open(os.path.join(dirpath, filename)) as fd:
                if not key.startswith("CONFIG_"):
                    raise Exception("Not sure how to handle Kconfig option that doesn't start with 'CONFIG_'")
                kconfig_key = key[len("CONFIG_"):]
                inside_option = False
                while True:
                    line = fd.readline()
                    # Empty lines have at least a '\n' in them.
                    if line == "":
                        break
                    line = line.rstrip()

                    if re.match("^config\s*%s(\s|$)" % kconfig_key, line):
                        inside_option = True
                        continue
                    elif re.match("^config ", line):
                        inside_option = False
                        continue

                    if not inside_option:
                        continue

                    while line.endswith("\\"):
                        line = line[:-1] + fd.readline().rstrip()

                    match = re.match("^\s*depends\s*on\s*(.+)", line)
                    if not match:
                        continue

                    for dependee in parse_dependencies(match.group(1), already_added):
                        add_kconfig_option("CONFIG_%s=y" % dependee, already_added)

    with open(args.defconfig_file, "a") as fd:
        fd.write("%s\n" % option)

def gather_currently_set_kconfig_options():
    set_options = dict()
    with open(args.defconfig_file) as fd:
        for line in fd.readlines():
            if line.strip() and not line.startswith("#"):
                key = line.split("=", 2)[0]
                if not key.startswith("CONFIG_"):
                    raise Exception("Not sure how to handle Kconfig option that doesn't start with 'CONFIG_'")
                # Add without "CONFIG_" prefix.
                key = key[len("CONFIG_"):]
                set_options[key] = True
    return set_options

already_added = gather_currently_set_kconfig_options()
add_kconfig_option(args.option[0], already_added)
