"""
    kampach.geometry
    ~~~~~~~~~~~~~~~~

    Building geometric shapes.

    :copyright: 2019 by Kampach Authors, see AUTHORS for more details.
    :license: CeCILL, see LICENSE for more details.
"""

from . import ureg, xmlio
from .arithmetic import parse_quantity
from abc import ABCMeta, abstractmethod
import xml.etree.ElementTree as ET
import math

null = 0*ureg.meter


class BuildingShape(metaclass=ABCMeta):
    """Abstract class describing a building shape, gathering the methods to
    compute volumes and areas.
    """
    
    def __init__(self, finish_thickness=null):
        self.finish_thickness = finish_thickness
    
    @abstractmethod
    def compute_total_volume(self):
        """Computes the total volume of the building.
        """
        pass
    
    def compute_fill_volume(self):
        """Computes the (inner) fill volume of the building.
        """
        return self.compute_total_volume()-self.compute_finish_volume()
    
    def compute_finish_volume(self):
        """Computes the (outer) finish volume of the building.
        """
        return self.compute_walls_finish_area()*self.finish_thickness
    
    @abstractmethod
    def compute_walls_finish_area(self):
        """Computes the (outer) finish area of the building walls.
        """
        pass
    
    @abstractmethod
    def compute_top_finish_area(self):
        """Computes the (outer) finish area of the building top.
        """
        pass
    
    def compute_total_finish_area(self):
        """Computes the total (outer) finish area of the building.
        """
        return self.compute_top_finish_area()+self.compute_walls_finish_area()
    
    def export_to_xml(self, parent):
        elem = ET.SubElement(parent, xmlio.get_tag_from_class(type(self)))
        elem.set('finish_thickness', str(self.finish_thickness))
        return elem
    
    def add_data_from_xml_element(self, elem):
        if 'finish_thickness' in elem.attrib:
            self.finish_thickness = parse_quantity(elem.get('finish_thickness'))


class TruncatedPyramid(BuildingShape):
    """A symmetric truncated pyramid with rectangular base.
    """
    
    def __init__(self, finish_thickness=null, bottom_length=null, bottom_width=null,
                 top_length=null, top_width=null, height=null):
        super().__init__(finish_thickness)
        self.bottom_width = bottom_width
        self.bottom_length = bottom_length
        self.top_width = top_width
        self.top_length = top_length
        self.height = height
    
    def compute_total_volume(self):
        """Computes the volume of the pyramid.
        """
#         B = self.bottom_width * self.bottom_length
#         b = self.top_width * self.top_length
#         #Use **.5 instead of math.sqrt for BoundedQuantity compatibility
#         vol = (B + b + (B*b)**.5) * self.height / 3.
#         return vol
        L = self.bottom_length
        l = self.top_length
        W = self.bottom_width
        w = self.top_width
        vol = w*l + ((W-w)*l + (L-l)*w)/2 + (L-l)*(W-w)/3
        vol *= self.height
        return vol 
    
    def compute_length_trapezoid_area(self):
        """Computes the area of the trapezoidal face along the length.
        """
        foot = 0.5 * abs(self.bottom_width - self.top_width)
        # Use **.5 instead of math.sqrt for BoundedQuantity compatibility
        height = (self.height*self.height + foot*foot)**.5
        return 0.5 * (self.bottom_length + self.top_length) * height
    
    def compute_width_trapezoid_area(self):
        """Computes the area of the trapezoidal face along the width.
        """
        foot = 0.5 * abs(self.bottom_length - self.top_length)
        # Use **.5 instead of math.sqrt for BoundedQuantity compatibility
        height = (self.height*self.height + foot*foot)**.5
        return 0.5 * (self.bottom_width + self.top_width) * height
    
    def compute_walls_finish_area(self):
        """Computes the area of the four trapezoidal faces of the pyramid.
        """
        area = self.compute_width_trapezoid_area()
        area += self.compute_length_trapezoid_area()
        area *= 2 # There are 4 faces
        return area
    
    def compute_top_finish_area(self):
        """Computes the area of the top base.
        """
        return self.top_length * self.top_width
    
    def export_to_xml(self, parent):
        elem = super().export_to_xml(parent)
        elem.set('bottom_length', str(self.bottom_length))
        elem.set('bottom_width', str(self.bottom_width))
        elem.set('top_length', str(self.top_length))
        elem.set('top_width', str(self.top_width))
        elem.set('height', str(self.height))
        return elem
    
    def add_data_from_xml_element(self, elem):
        super().add_data_from_xml_element(elem)
        if 'bottom_length' in elem.attrib:
            self.bottom_length = parse_quantity(elem.get('bottom_length'))
        if 'bottom_width' in elem.attrib:
            self.bottom_width = parse_quantity(elem.get('bottom_width'))
        if 'top_length' in elem.attrib:
            self.top_length = parse_quantity(elem.get('top_length'))
        if 'top_width' in elem.attrib:
            self.top_width = parse_quantity(elem.get('top_width'))
        if 'height' in elem.attrib:
            self.height = parse_quantity(elem.get('height'))


class Cuboid(TruncatedPyramid):
    """A rectangular cuboid.
    """
    
    def __init__(self, finish_thickness=null, length=null, width=null, height=null):
        super().__init__(finish_thickness, length, width, length, width, height)
    
    def export_to_xml(self, parent):
        elem = super(TruncatedPyramid, self).export_to_xml(parent)
        elem.set('length', str(self.bottom_length))
        elem.set('width', str(self.bottom_width))
        elem.set('height', str(self.height))
        return elem
    
    def add_data_from_xml_element(self, elem):
        super().add_data_from_xml_element(elem)
        if 'length' in elem.attrib:
            length = parse_quantity(elem.get('length'))
        if 'width' in elem.attrib:
            width = parse_quantity(elem.get('width'))
        self.__init__(self.finish_thickness, length, width, self.height)


class Prism(TruncatedPyramid):
    """A prism, like a roof top. The top edge is along the width
    """
    
    def __init__(self, finish_thickness=null, width=null, depth=null, height=null):
        super().__init__(finish_thickness, width, depth, width, null, height)
    
    def export_to_xml(self, parent):
        elem = super(TruncatedPyramid, self).export_to_xml(parent)
        elem.set('width', str(self.bottom_length))
        elem.set('depth', str(self.bottom_width))
        elem.set('height', str(self.height))
        return elem
    
    def add_data_from_xml_element(self, elem):
        super().add_data_from_xml_element(elem)
        if 'width' in elem.attrib:
            width = parse_quantity(elem.get('width'))
        if 'depth' in elem.attrib:
            depth = parse_quantity(elem.get('depth'))
        self.__init__(self.finish_thickness, width, depth, self.height)


class Stairs(TruncatedPyramid):
    """Stairs.
    """
    
    def __init__(self, finish_thickness=null, bottom_length=null, bottom_width=null,
                 top_length=null, top_width=null, height=null, depth=null):
        super().__init__(finish_thickness, bottom_length, bottom_width,
                         top_length, top_width, height)
        self.depth = depth
    
    def compute_finish_volume_base_area(self):
        """Computes the area of the two trapezoidal side faces of the stairs,
        plus the area of the countersteps (area of the finish volume).
        """
        area = 2*self.compute_width_trapezoid_area()
        area += 0.5*(self.bottom_length+self.top_length)*self.height
        return area
    
    def compute_finish_volume(self):
        """For stairs, the finish volume is not the walls finish area times
        the finish thickness, because the horizontal steps are not taken into
        account.
        """
        return self.compute_finish_volume_base_area()*self.finish_thickness
    
    def compute_walls_finish_area(self):
        """Computes the area covered by plaster: add the horizontal steps to
        the base area of the finish volume.
        """
        area = self.compute_finish_volume_base_area()
        area += 0.5*(self.bottom_length+self.top_length)*self.depth
        return area
    
    def export_to_xml(self, parent):
        elem = super().export_to_xml(parent)
        elem.set('depth', str(self.depth))
        return elem
    
    def add_data_from_xml_element(self, elem):
        super().add_data_from_xml_element(elem)
        self.depth = parse_quantity(elem.get('depth'))


class Cylinder(BuildingShape):
    """A cylinder.
    """
    
    def __init__(self, finish_thickness=null, diameter=null, height=null):
        super().__init__(finish_thickness)
        self.radius = diameter/2.
        self.height = height
    
    def compute_total_volume(self):
        """Computes the volume of the cylinder.
        """
        return self.height * math.pi * self.radius * self.radius
    
    def compute_walls_finish_area(self):
        """Computes the area of the vertical face.
        """
        return 2 * math.pi * self.radius * self.height
    
    def compute_top_finish_area(self):
        """Computes the area of the top base.
        """
        return math.pi * self.radius * self.radius
    
    def export_to_xml(self, parent):
        elem = super().export_to_xml(parent)
        elem.set('diameter', str(2 * self.radius))
        elem.set('height', str(self.height))
        return elem
    
    def add_data_from_xml_element(self, elem):
        super().add_data_from_xml_element(elem)
        if 'diameter' in elem.attrib:
            self.radius = parse_quantity(elem.get('diameter')) / 2
        if 'height' in elem.attrib:
            self.height = parse_quantity(elem.get('height'))


class Superstructure(BuildingShape):
    """A superstructure like the ones on top of pyramids.
    """
    
    def __init__(self, finish_thickness=null, number_of_rooms=2, depth=null,
                 width=null, walls_thickness=null, door_width=null, door_height=null,
                 ceiling_height=null, outer_height=null):
        super().__init__(finish_thickness)
        self.number_of_rooms = number_of_rooms
        self.depth = depth
        self.width = width
        self.walls_thickness = walls_thickness
        self.door_width = door_width
        self.door_height = door_height
        self.ceiling_height = ceiling_height
        self.outer_height = outer_height
    
    def compute_room_depth(self):
        room_depth = self.depth-2*self.walls_thickness
        room_depth -= (self.number_of_rooms-1)*self.walls_thickness
        room_depth /= self.number_of_rooms
        return room_depth
    
    def compute_room_width(self):
        return self.width-2*self.walls_thickness
    
    def compute_total_volume(self):
        prism = Prism(width=self.compute_room_width(),
                      depth=self.compute_room_depth(),
                      height=self.ceiling_height-self.door_height).compute_total_volume()
        room = Cuboid(length=self.compute_room_width(),
                      width=self.compute_room_depth(),
                      height=self.door_height).compute_total_volume()
        door = Cuboid(length=self.door_width,
                      width=self.walls_thickness,
                      height=self.door_height).compute_total_volume()
        vol_sub = self.number_of_rooms*(prism+room+door)
        vol = self.outer_height*self.width*self.depth
        return vol-vol_sub
    
    def compute_walls_finish_area(self):
        outer_area = self.outer_height*(2*(self.width+self.depth)-self.door_width)
        
        inner_walls_area = 2*(self.depth-self.walls_thickness)
        inner_walls_area += self.width-2*self.walls_thickness
        l = self.width-2*self.walls_thickness-self.door_width
        inner_walls_area += l*(1+2*(self.number_of_rooms-1))
        inner_walls_area *= self.door_height
        
        prism = Prism(width=self.compute_room_width(),
                      depth=self.compute_room_depth(),
                      height=self.ceiling_height-self.door_height)
        ceiling_area = self.number_of_rooms*prism.compute_walls_finish_area()
        
        return outer_area+inner_walls_area+ceiling_area
    
    def compute_top_finish_area(self):
        return self.width*self.depth
    
    def export_to_xml(self, parent):
        elem = super().export_to_xml(parent)
        elem.set('number_of_rooms', str(self.number_of_rooms))
        elem.set('depth', str(self.depth))
        elem.set('width', str(self.width))
        elem.set('walls_thickness', str(self.walls_thickness))
        elem.set('door_width', str(self.door_width))
        elem.set('door_height', str(self.door_height))
        elem.set('ceiling_height', str(self.ceiling_height))
        elem.set('outer_height', str(self.outer_height))
        return elem
    
    def add_data_from_xml_element(self, elem):
        super().add_data_from_xml_element(elem)
        if 'number_of_rooms' in elem.attrib:
            self.number_of_rooms = parse_quantity(elem.get('number_of_rooms'))
        if 'depth' in elem.attrib:
            self.depth = parse_quantity(elem.get('depth'))
        if 'width' in elem.attrib:
            self.width = parse_quantity(elem.get('width'))
        if 'walls_thickness' in elem.attrib:
            self.walls_thickness = parse_quantity(elem.get('walls_thickness'))
        if 'door_width' in elem.attrib:
            self.door_width = parse_quantity(elem.get('door_width'))
        if 'door_height' in elem.attrib:
            self.door_height = parse_quantity(elem.get('door_height'))
        if 'ceiling_height' in elem.attrib:
            self.ceiling_height = parse_quantity(elem.get('ceiling_height'))
        if 'outer_height' in elem.attrib:
            self.outer_height = parse_quantity(elem.get('outer_height'))
