"""
    Kampach main script.

    :copyright: 2019 by Kampach Authors, see AUTHORS for more details.
    :license: CeCILL, see LICENSE for more details.
"""

from kampach.xmlio import load_xml_file
from kampach.valuable import Valuable

root_valuable = None
while root_valuable is None:
    try:
        filename = input('Enter the file name or \'stop\'.')
        if filename.lower() == 'stop':
            break
    except EOFError:
        break
    try:
        root_valuable = load_xml_file(filename)
    except FileNotFoundError:
        print('File not found.')

if isinstance(root_valuable, Valuable):
    total_cost = root_valuable.compute_total_cost()
    print()
    print("Total cost: {}".format(total_cost))
    print()
    input('Press <Enter> to terminate.')