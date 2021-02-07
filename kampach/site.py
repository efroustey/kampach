"""
    kampach.site
    ~~~~~~~~~~~~

    Definition of Site, Building and Activities.

    :copyright: 2019 by Kampach Authors, see AUTHORS for more details.
    :license: CeCILL, see LICENSE for more details.
"""

from . import ureg, xmlio, valuable
from .arithmetic import parse_quantity
import xml.etree.ElementTree as ET


class Site(valuable.Valuable):
    """An archeological site. Contains buildings and geographical information.
    """
    
    def __init__(self, name=''):
        super().__init__(name)
    
    def compute_own_cost(self, print_depth=0, geom_csv=None, cost_csv=None):
        return 0


class SuperBuilding(valuable.Valuable):
    """
    """
    
    def __init__(self, name=''):
        super().__init__(name)
    
    def compute_own_cost(self, print_depth=0, geom_csv=None, cost_csv=None):
        return 0


class Building(valuable.Valuable):
    """An archeological building. Has a shape and possibly substructures.
    """
    
    def __init__(self, name='', shape=None):
        super().__init__(name)
        self.shape = shape
        self.substructures = []
    
    @property
    def shape(self):
        """A BuildingShape object.
        """
        return self._shape
    
    @property
    def substructures(self):
        """A list of (older) structures inside/below this building.
        """
        return self._substructures
    
    @property
    def total_volume(self):
        """The total volume of the building, including any substructure.
        """
        return self.shape.compute_total_volume()
    
    @property
    def fill_volume(self):
        """The (inner) fill volume of the building.
        """
        vol = self.shape.compute_fill_volume()
        for b in self.substructures:
            vol -= b.compute_total_volume()
        return vol
    
    @property
    def finish_volume(self):
        """The finish (outer) volume of the building.
        """
        return self.shape.compute_finish_volume()
    
    @property
    def total_finish_area(self):
        """The finish (outer) area of the building.
        """
        return self.shape.compute_total_finish_area()
    
    @property
    def top_finish_area(self):
        """The finish (outer) area of the building top.
        """
        return self.shape.compute_top_finish_area()
    
    @property
    def walls_finish_area(self):
        """The finish (outer) area of the building walls.
        """
        return self.shape.compute_walls_finish_area()
    
    @shape.setter
    def shape(self, val):
        self._shape = val
    
    @substructures.setter
    def substructures(self, val):
        self._substructures = val
    
    def compute_own_cost(self, print_depth=0, geom_csv=None, cost_csv=None):
        if self.name:
            blank = " "*2*print_depth
            print()
            print(blank + self.name)
            print(blank + '='*len(self.name))
            print(blank + 'Fill volume: {}'.format(self.fill_volume))
            print(blank + 'Finish volume: {}'.format(self.finish_volume))
            print(blank + 'Total finish area: {}'.format(self.total_finish_area))
            print(blank + 'Top finish area: {}'.format(self.top_finish_area))
            print(blank + 'Walls finish area: {}'.format(self.walls_finish_area))
            if geom_csv:
                geom_csv.writerow(self.format_geom_data())
            if cost_csv:
                cost_csv.writerow([self.name])
        return 0

    def format_geom_data(self):
        row = [self.name] + self.fill_volume.as_list() + self.finish_volume.as_list()
        row += self.total_finish_area.as_list() + self.top_finish_area.as_list()
        row += self.walls_finish_area.as_list()
        return row

    @staticmethod
    def make_geom_csv_header():
        return ['Name', 'Fill volume min', 'Fill volume int', 'Fill volume max',
                'Finish volume min', 'Finish volume int', 'Finish volume max',
                'Total finish area min', 'Total finish area int', 'Total finish area max',
                'Top finish area min', 'Top finish area int', 'Top finish area max',
                'Walls finish area min', 'Walls finish area int', 'Walls finish area max']
    
    def export_to_xml(self, parent=None):
        elem = super().export_to_xml(parent)
        shape = ET.SubElement(elem, 'Shape')
        self.shape.export_to_xml(shape)
        if self.substructures:
            substructures = ET.SubElement(elem, 'Substructures')
            for s in self.substructures:
                s.export_to_xml(substructures)
        return elem
    
    def add_data_from_xml_element(self, elem):
        super().add_data_from_xml_element(elem)
        shape = elem.find('Shape')
        if shape:
            self.shape = xmlio.create_object_from_xml_element(shape[0])
        substructures = elem.find('Substructures')
        if substructures:
            for s in substructures:
                structure = xmlio.create_object_from_xml_element(s)
                self.substructures.append(structure)
            

class TransportActivity(valuable.LinearQuantitativeValuable):
    """Transport of material.
    """
    
    def __init__(self, name='', amount=None, amount_per_travel=None,
                 speed_loaded=None, speed_empty=None, distance=None):
        super(valuable.LinearQuantitativeValuable, self).__init__(name, amount)
        self.amount_per_travel = amount_per_travel
        self.speed_loaded = speed_loaded
        self.speed_empty = speed_empty
        self.distance = distance
    
    @property
    def marginal_cost(self):
        """The cost of transportation is a standard United Nations formula.
        """
        travel_time = self.distance * (1/self.speed_empty +
                                       1/self.speed_loaded)
        return (travel_time / self.amount_per_travel).to(ureg.work_day /
                                                         self.amount.units)
    
    @property
    def fixed_cost(self):
        """Overriden from LinearQuantitativeValuable
        """
        return 0
    
    @property
    def amount_per_travel(self):
        """Amount of material carried at each travel.
        """
        return self._amount_per_travel
    
    @property
    def speed_loaded(self):
        """Moving speed when carrying the material.
        """
        return self._speed_loaded
    
    @property
    def speed_empty(self):
        """Moving speed when carrying nothing.
        """
        return self._speed_empty
    
    @property
    def distance(self):
        """Distance to run at each travel (one way.)
        """
        return self._distance
    
    @marginal_cost.setter
    def marginal_cost(self, val):
        # Don't allow to set the marginal cost directly
        pass
    
    @fixed_cost.setter
    def fixed_cost(self, val):
        self._fixed_cost = val
    
    @amount_per_travel.setter
    def amount_per_travel(self, val):
        self._amount_per_travel = val
    
    @speed_loaded.setter
    def speed_loaded(self, val):
        self._speed_loaded = val
    
    @speed_empty.setter
    def speed_empty(self, val):
        self._speed_empty = val
    
    @distance.setter
    def distance(self, val):
        self._distance = val
    
    def export_to_xml(self, parent=None):
        elem = super(valuable.LinearQuantitativeValuable,
                     self).export_to_xml(parent)
        elem.set('amount_per_travel', str(self.amount_per_travel))
        elem.set('speed_loaded', str(self.speed_loaded))
        elem.set('speed_empty', str(self.speed_empty))
        elem.set('distance', str(self.distance))
        return elem
    
    def add_data_from_xml_element(self, elem):
        super(valuable.LinearQuantitativeValuable,
              self).add_data_from_xml_element(elem)
        self.amount_per_travel = parse_quantity(elem.get('amount_per_travel'))
        self.speed_loaded = parse_quantity(elem.get('speed_loaded'))
        self.speed_empty = parse_quantity(elem.get('speed_empty'))
        self.distance = parse_quantity(elem.get('distance'))


class ProductionActivity(valuable.LinearQuantitativeValuable):
    pass
