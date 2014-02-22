"""
Adds StatCounter Code snippets at the end of specified HTML files
"""
import sys
import os
import os.path
import shutil
import tempfile
import csv
import argparse
import re
import logging

LOG_LEVEL = logging.INFO

SC_CODE_TEMPLATE = """
<!-- Start of StatCounter Code for Default Guide -->

<script type="text/javascript">
  var sc_project={sc_project:s}; var sc_invisible=1; var
  sc_security="{sc_security:s}"; var scJsHost = (("https:" == document.location.protocol) ? "https://secure." : "http://www."); document.write("<sc"+"ript type='text/javascript' src='" + scJsHost+ "statcounter.com/counter/counter.js'></"+"script>");
</script>

<noscript>
  <div class="statcounter">
    <a title="web counter" href="http://statcounter.com/free-hit-counter/"
      target="_blank"><img class="statcounter"
      src="http://c.statcounter.com/{sc_project:s}/0/{sc_security:s}/1/" alt="web counter">
    </a>
  </div>
</noscript>

 <!-- End of StatCounter Code for Default Guide -->
 """


def read_sc_codes(ifo):
    """
    Reads ifo (file object open for reading) with StatCounter codes. Each
    line in inFile must have the following four comma separated fields:

    - file name, incl. extension; files containing spaces need enclosed in
            double quotes
    - path relative to the root directory that passed as a command line
            argument to statcounter.py (e.g. _build/html): enclose in double
            quotes if it contains spaces
    - SC project code
    - SC security code

    Returns a dictionary keyed by os.path.join(<path>, <file name>); values are
    dictionaries with keys 'sc_project' and 'sc_security'.
    """
    emptyLine = re.compile('^[\s]*$')
    lines = csv.reader(ifo, delimiter=',', skipinitialspace=True,
            quotechar='"')
    out = {}
    for rec in lines:
        logging.debug("%20s: rec = %s" % ('read_sc_codes', rec))
        if not rec or emptyLine.match(rec[0]) or rec[0].startswith('#'):
            continue
        key = os.path.join(rec[1], rec[0])
        out[key] = {'sc_project': rec[2], 'sc_security': rec[3]}

    return out


def insert_sc_script(htFile, sc_code_dict):
    """
    Inserts  StatCounter script before the closing </body> tag of htFile unless
    the line containing the closing body tag has any non-whitespace text in
    front of that tag. sc_code_dict is a dictionary providing the keys and
    values required by the template script string. Returns True if the script
    was inserted, False otherwise.
    """
    genMsg = ("<!-- StatCounter JavaScript code snippet automatically "
              "inserted by %s -->" % __file__)
    bodyCloseTag = re.compile(r'^\s*<\s*/\s*body\s*>')
    existingCode = re.compile(r'statcounter')
    tmpFD, tmpFile = tempfile.mkstemp(prefix='statcounter_', text=True)
    os.close(tmpFD)
    tfo = open(tmpFile, 'w')
    with open(htFile, 'r') as htFO:
        logging.debug("%20s: processing file %s" % ('append_sc_script',
                      htFile))
        inserted = False
        for line in htFO:
            if existingCode.search(line):
                inserted = False
                break
            if bodyCloseTag.match(line):
                tfo.write(genMsg)
                tfo.write(SC_CODE_TEMPLATE.format(**sc_code_dict))
                inserted = True
            tfo.write(line)
    tfo.close()
    if inserted:
        shutil.move(tmpFile, htFile)
    elif os.path.exists(tmpFile):
        os.unlink(tmpFile)

    return inserted


def update_ht_files(scDict, rootDir):
    """
    Will iterate over all files in scDict and call append_sc_script to insert
    StatCounter script. Returns a dictionary with all files it iterated over as
    keys. Values will 'True' if StatCounter script was inserted for that file,
    'False' if not.
    """
    results = {}
    for htFile in scDict:
        results[htFile] = insert_sc_script(os.path.join(rootDir, htFile),
                                           scDict[htFile])
    return results


if __name__ == '__main__':

    logging.basicConfig(level=LOG_LEVEL)

    script = os.path.basename(__file__)

    parser = argparse.ArgumentParser(description="""
    %s -- Inserts StatCounter script snippets in HTML files
    """ % script)
    parser.add_argument('--sclist', metavar='FILE',
            type=argparse.FileType('r'), default=sys.stdin, help="Comma "
            "separated input file, listing file name, directory path "
            "(relative to basedir), and StatCounter project and security "
            "codes for  each file into which the StatCounter script is to be "
            "inserted. Defaults to stdin.")
    parser.add_argument('--basedir', metavar='DIR', required=True,
            help="Base directory against which the path entries in sclist "
            "are provided (e.g. _build/html).")

    args = parser.parse_args()

    scDict = read_sc_codes(args.sclist)
    args.sclist.close()
    results = update_ht_files(scDict, args.basedir)
    failed = [f for f in results if not results[f]]

    if failed:
        for f in failed:
            logging.warning("%20s: no script code inserted into %s" % (script, f))

    logging.info("%s: updated %d files" % (script, len(results) - len(failed)))
