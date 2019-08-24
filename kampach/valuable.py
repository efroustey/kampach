"""
    kampach.valuable
    ~~~~~~~~~~~~~~~~

    Valuable objects have a cost that is computed as their own cost
    plus the sum of their inputs' costs.

    :copyright: 2019 by Kampach Authors, see AUTHORS for more details.
    :license: CeCILL, see LICENSE for more details.
"""

from . import xmlio
from abc import ABCMeta, abstractmethod
import xml.etree.ElementTree as ET
from .arithmetic import parse_quantity
from pint.errors import UndefinedUnitError


class Valuable(metaclass=ABCMeta):
    """Abstract class representing an object having a cost.
    
    Implementation classes must override the compute_own_cost() method.
    """
    
    def __init__(self, name=''):
        self.inputs = []
        self.name = name
        
    def __repr__(self):
        return "<{0}: {1}>".format(type(self).__name__, self.name)
    
    @property
    def name(self):
        """Name of the valuable.
        """
        return self._name
        
    @property
    def inputs(self):
        """List of Valuable or QuantitativeValuableInput objects
        """
        return self._inputs
    
    @name.setter
    def name(self, val):
        self._name = val
    
    @inputs.setter
    def inputs(self, vals):
        self._inputs = vals
    
    def compute_total_cost(self, print_depth=0):
        """Computes the total cost of this valuable, including the cost of its
        inputs.
        """
        cost = self.compute_own_cost(print_depth)
        cost += sum(map(lambda i: i.compute_total_cost(print_depth+1), self.inputs))
        return cost
    
    @abstractmethod
    def compute_own_cost(self, print_depth=0):
        """Computes the cost of this valuable without its inputs.
        """
        pass

    def export_to_xml(self, parent=None):
        tag = xmlio.get_tag_from_class(type(self))
        attrib = {'name': self.name}
        if parent is None:
            elem = ET.Element(tag, attrib)
        else:
            elem = ET.SubElement(parent, tag, attrib)
        if self.inputs:
            inputs = ET.SubElement(elem, 'Inputs')
            for i in self.inputs:
                i.export_to_xml(inputs)
        return elem
    
    def add_data_from_xml_element(self, elem):
        if 'name' in elem.attrib.keys():
            self.name = elem.attrib['name']
        inputs = elem.find('Inputs')
        if inputs:
            for i in inputs:
                input_val = xmlio.create_object_from_xml_element(i)
                self.inputs.append(input_val)
                if isinstance(input_val, LinearQuantitativeValuableInput):
                    input_val.target_valuable = self


class QuantitativeValuable(Valuable, metaclass=ABCMeta):
    """Abstract class representing an object having a proper cost related to
    its quantity.
     
    Implementation classes must override compute_own_cost()
    """
    
    def __init__(self, name='', amount=0):
        super().__init__(name)
        self.amount = amount
    
    @property
    def amount(self):
        """Amount of valuable object.
        """
        return self._amount
    
    @amount.setter
    def amount(self, val):
        self._amount = val


class DefaultQuantitativeValuable(QuantitativeValuable):
    """Default implementation of QuantitativeValuable with null proper cost.
    """
    
    def compute_own_cost(self, print_depth=0):
        return 0


class LinearQuantitativeValuable(QuantitativeValuable):
    """Object having a proper cost linearly related to its quantity.
    """
    
    def __init__(self, name='', amount=0, marginal_cost=1, fixed_cost=0):
        super().__init__(name, amount)
        self.marginal_cost = marginal_cost
        self.fixed_cost = fixed_cost
    
    @property
    def marginal_cost(self):
        """Cost of a unitary amount of this valuable object.
        """
        return self._marginal_cost
    
    @property
    def fixed_cost(self):
        """Fixed cost of this valuable object.
        """
        return self._fixed_cost
    
    @marginal_cost.setter
    def marginal_cost(self, val):
        self._marginal_cost = val
    
    @fixed_cost.setter
    def fixed_cost(self, val):
        self._fixed_cost = val
    
    def compute_own_cost(self, print_depth=0):
        cost = self.amount*self.marginal_cost + self.fixed_cost
        if self.name:
            blank = " "*2*print_depth
            print()
            print(blank + self.name)
            print(blank + '='*len(self.name))
            print(blank + 'Amount: {}'.format(self.amount))
            print(blank + 'Cost: {}'.format(cost))
        return cost
    
    def export_to_xml(self, parent=None):
        elem = super().export_to_xml(parent)
        if self.marginal_cost != 1:
            elem.set('marginal_cost', str(self.marginal_cost))
        if self.fixed_cost != 0:
            elem.set('fixed_cost', str(self.fixed_cost))
        return elem
    
    def add_data_from_xml_element(self, elem):
        super().add_data_from_xml_element(elem)
        if 'marginal_cost' in elem.attrib.keys():
            self.marginal_cost = parse_quantity(elem.get('marginal_cost'))
        if 'fixed_cost' in elem.attrib.keys():
            self.fixed_cost = parse_quantity(elem.get('fixed_cost'))


class QuantitativeValuableInput(metaclass=ABCMeta):
    """Abstract class representing the input of a target valuable object.
    It used when the required amount of input is related to the target.
    
    Implementation classes must override the compute_total_cost() method.
    """
    
    def __init__(self, target_valuable=None, input_valuable=None,
                 target_amount='amount'):
        self.target_valuable = target_valuable
        self.input_valuable = input_valuable
        self.target_amount = target_amount
    
    @property
    def target_valuable(self):
        """Valuable object.
        """
        return self._target_valuable
    
    @property
    def input_valuable(self):
        """QuantitativeValuable object.
        """
        return self._input_valuable
    
    @property
    def target_amount(self):
        """Property of the target valuable required to compute the input
        amount.
        """
        return self._target_amount
    
    @target_valuable.setter
    def target_valuable(self, val):
        self._target_valuable = val
    
    @input_valuable.setter
    def input_valuable(self, val):
        self._input_valuable = val
    
    @target_amount.setter
    def target_amount(self, val):
        self._target_amount = val
    
    @abstractmethod
    def compute_total_cost(self):
        """Computes the total cost of the input valuable.
        """
        pass
    
    @abstractmethod
    def export_to_xml(self, parent):
        pass
    
    @abstractmethod
    def add_data_from_xml_element(self, elem):
        pass


class LinearQuantitativeValuableInput(QuantitativeValuableInput):
    """Input of a target valuable object. The required amount of input is
    linearly related to the target.
    """
    
    def __init__(self, target_valuable=None, input_valuable=None,
                 target_amount='amount', marginal_amount=1., fixed_amount=0.):
        super().__init__(target_valuable, input_valuable, target_amount)
        self.marginal_amount = marginal_amount
        self.fixed_amount = fixed_amount
    
    @property
    def marginal_amount(self):
        """Amount required for a unitary target amount.
        """
        return self._marginal_amount
    
    @property
    def fixed_amount(self):
        """Fixed amount required.
        """
        return self._fixed_amount
    
    @marginal_amount.setter
    def marginal_amount(self, val):
        self._marginal_amount = val
    
    @fixed_amount.setter
    def fixed_amount(self, val):
        self._fixed_amount = val
    
    def compute_total_cost(self, print_depth=0):
        if isinstance(self.target_amount, str):
            target_amount = getattr(self.target_valuable, self.target_amount)
        else:
            target_amount = self.target_amount
        self.input_valuable.amount = target_amount*self.marginal_amount
        self.input_valuable.amount += self.fixed_amount
        return self.input_valuable.compute_total_cost(print_depth)
    
    def export_to_xml(self, parent):
        tag = xmlio.get_tag_from_class(type(self))
        elem = ET.SubElement(parent, tag)
        if self.marginal_amount != 1:
            elem.set('marginal_amount', str(self.marginal_amount))
        if self.target_amount != 'amount':
            elem.set('target_amount', self.target_amount)
        if self.fixed_amount != 0:
            elem.set('fixed_amount', str(self.fixed_amount))
        self.input_valuable.export_to_xml(elem)
        return elem
    
    def add_data_from_xml_element(self, elem):
        if 'target_amount' in elem.attrib.keys():
            try:
                # For custom target amount directly specified in XML file
                self.target_amount = parse_quantity(elem.get('target_amount'))
            except UndefinedUnitError:
                # Normal behaviour
                self.target_amount = elem.get('target_amount')
        if 'marginal_amount' in elem.attrib.keys():
            self.marginal_amount = parse_quantity(elem.get('marginal_amount'))
        if 'fixed_amount' in elem.attrib.keys():
            self.fixed_amount = parse_quantity(elem.get('fixed_amount'))
        self.input_valuable = xmlio.create_object_from_xml_element(elem[0])
