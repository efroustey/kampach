"""
    kampach.xmlio
    ~~~~~~~~~~~~~

    XML input/output.

    :copyright: 2019 by Kampach Authors, see AUTHORS for more details.
    :license: CeCILL, see LICENSE for more details.
"""

# Import all the classes that can be instantiated
from .geometry import BuildingShape, Cuboid, Prism, TruncatedPyramid, Stairs, Superstructure
from .site import Building, ProductionActivity, Site, SuperBuilding, TransportActivity
from .valuable import LinearQuantitativeValuableInput

import xml.etree.ElementTree as ET
import xml.dom.minidom


"""List (XMLTagName, Class)
"""
XML_NAMES = (('BuildingShape', BuildingShape),
             ('Cuboid', Cuboid),
             ('Prism', Prism),
             ('TruncatedPyramid', TruncatedPyramid),
             ('Stairs', Stairs),
             ('Superstructure', Superstructure),
             ('Building', Building),
             ('SuperBuilding', SuperBuilding),
             ('ProductionActivity', ProductionActivity),
             ('Site', Site),
             ('TransportActivity', TransportActivity),
             ('LinearInput', LinearQuantitativeValuableInput),
             )


def get_tag_from_class(cls):
    for tag, _cls in XML_NAMES:
        if _cls == cls:
            return tag


def get_class_from_tag(tag):
    for _tag, cls in XML_NAMES:
        if _tag == tag:
            return cls
    raise ValueError('Unrecognized XML tag: ' + tag)


def create_object_from_xml_element(elem):
    obj = get_class_from_tag(elem.tag)()
    obj.add_data_from_xml_element(elem)
    return obj


def save_xml_file(root, filename):
    xml_root = root.export_to_xml()
    rough_string = ET.tostring(xml_root)
    reparsed = xml.dom.minidom.parseString(rough_string)
    reparsed.toprettyxml()
    f = open(filename, 'w')
    reparsed.writexml(f, indent='', addindent='\t', newl='\n')
    f.close()


def load_xml_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    return create_object_from_xml_element(root)



















