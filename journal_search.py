# -*- coding: utf-8 -*-
##

"""Simple workaround to search an display journal records from labs"""

import re, sys
import requests
import getopt

INSPIRE_API_ENDPOINT = "https://inspirehep.net/api"


def _usage():
    print(
        """Example:\
python journal_search.py Phys Rev
Possible arguments:
-n , --name:   short_title, journal_title, title_variants
-e , --exact:  short_title, journal_title only
-l , --long:   print all fields
-a , --all:    print all records (default up to 20)
"""
    )


fields_short = [
    "self",
    "short_title",
    "journal_title",
    "urls",
]

fields_long = [
    "control_number",
    "self",
    "short_title",
    "journal_title",
    "title_variants",
    "empty_line",
    "_harvesting_info",
    "publisher",
    "urls",
    "doi_prefixes",
    "empty_line",
    "inspire_categories",
    "issns",
    "license",
    "proceedings",
    "public_notes",
    "_private_notes",
    "refereed",
    "empty_line",
    "date_ended",
    "date_started",
    "deleted",
    "deleted_records",
    "new_record",
    "related_records",
    "legacy_creation_date",
    "legacy_version",
]


def normalize_name(string):
    """Strip punktuation"""
    norm_name = re.sub("[., ]+", " ", string).lower()
    return norm_name


def _read_options(options_in):
    """Reads the options and generate search_pattern and flags"""

    flags = {"value": "", "exact": False, "name": False, "long": False, "all": False}
    options = {
        "-e": "exact",
        "--exact": "exact",
        "-n": "name",
        "--name": "name",
        "-l": "long",
        "--long": "long",
        "-a": "all",
        "--all": "all",
    }

    options_string = options_in[1:]
    try:
        short_flags = "nelah"
        long_flags = ["name", "exact", "long", "all", "help"]
        opts, args = getopt.gnu_getopt(options_string, short_flags, long_flags)
    except getopt.GetoptError as err1:
        print("Options problem: %s" % err1, file=sys.stderr)
        _usage()

    if not args:
        _usage()
        sys.exit(0)

    flags["value"] = " ".join(args)

    for option, argument in opts:
        if option in ("-h", "--help"):
            _usage()
            sys.exit(0)
        elif option in options:
            flags[options[option]] = True
        else:
            # This shouldn't happen as gnu_getopt should already handle
            # that case.
            print("option unrecognized -- %s" % option)

    return flags


def perform_inspire_search(query, facets=None, collection="journals"):
    """Perform the search query on INSPIRE.

    Args:
        query (str): the query to perform
        facets (dict): mapping of facet filters to values
        collection (str): collection to search in

    Yields:
        the json response for every record.
    """
    facets = facets or {}
    response = requests.get(
        "%s/%s" % (INSPIRE_API_ENDPOINT, collection), params={"q": query}, verify=False
    )

    response.raise_for_status()
    content = response.json()

    for result in content["hits"]["hits"]:
        yield result

    while "next" in content.get("links", {}):
        response = requests.get(content["links"]["next"], verify=False)
        response.raise_for_status()
        content = response.json()

        for result in content["hits"]["hits"]:
            yield result


def print_dict(value, format):
    """Print values which are dict in given format"""
    if type(value) != dict:
        return format % value

    primary_key = "value"
    keys = list(value.keys())
    text = ""
    if primary_key in keys:
        keys.remove(primary_key)
        text += format % value[primary_key]
    for key in keys:
        if key in format:
            this_text = "%s" % value[key]
        else:
            this_text = "%s : %s" % (key, value[key])
        text += format % this_text
    return text


def print_list(value, format):
    """Print values which are list in given format"""
    if type(value) != list:
        return format % value

    text = ""
    for item in value:
        if type(item) == dict:
            format = format.rstrip()
            prefix = format.rsplit(" : ", 1)
            if len(prefix) == 2:
                text += "%s : " % prefix[0]
                text += print_dict(item, prefix[1] + " ;  ")
            else:
                text += print_dict(item, format + " ;  ")
            text += "\n"
        else:
            text += format % item
    return text


def print_journal(metadata, fields):
    """Simple print json of a record"""
    text = ""
    format = "%25s : %%s\n"

    for field in fields:
        if field == "empty_line":
            text += "\n"
        elif field in metadata:
            value = metadata[field]
            if type(value) == list:
                text += print_list(value, format % field)
            elif type(value) == dict:
                text += print_dict(value, format % field)
            else:
                text += format % field % value
    return text


def get_journals(flags):
    """Search for journals depending on arguments, return list of ASCII representation"""
    result = []

    name = flags["value"]
    name_fields = ["journal_title.title", "short_title"]
    search_pattern = " OR ".join(['%s:"%s"' % (field, name) for field in name_fields])
    if flags["exact"]:
        pass
    elif flags["name"]:
        search_pattern += ' OR title_variants:"%s"' % normalize_name(name)
    else:
        search_pattern = name

    if flags["long"]:
        fields = fields_long
    else:
        fields = fields_short

    print("\n%s\n" % search_pattern)
    for record in perform_inspire_search(search_pattern):
        if "metadata" in record:
            result.append(print_journal(record["metadata"], fields))

    if not result:
        result.append(
            "No records found for\nhttps://inspirehep.net/api/journals?q=%s\n"
            % search_pattern
        )
    return result


def main():
    """Parse options, search journals, print result"""
    flags = _read_options(sys.argv)
    result = get_journals(flags)

    if len(result) > 20 and not flags["all"]:
        print("\n\n%s records -refine your search or use -a" % len(result))
        _usage()
        exit()

    print("\n\n\n")
    for journal in result:
        print(journal)
        print("==================")


if __name__ == "__main__":
    main()
