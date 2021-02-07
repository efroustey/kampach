"""
    kampach.arithmetic
    ~~~~~~~~~~~~~~~~~~

    Definition of the BoundedQuantity object that handles quantities with
    min and max incertitude bounds.

    :copyright: 2019 by Kampach Authors, see AUTHORS for more details.
    :license: CeCILL, see LICENSE for more details.
"""

from numbers import Number
from . import ureg
import operator
import copy


def parse_quantity(string):
    if not ',' in string:
        if '[' in string or ']' in string:
            raise ValueError('Missing comma in: ' + string)
        val = ureg(string)
        if not isinstance(val, Number):
            val = BoundedQuantity(val)
    else:
        spl = string.split(',')
        if len(spl) == 2:
            val = BoundedQuantity(ureg(spl[0]))
            bounds = spl[1].strip('[ ]').split(';')
            val.lower = float(bounds[0])
            val.upper = float(bounds[1])
        else:
            raise ValueError('can\'t parse a string with multiple commas: ' + string)
    return val


class BoundedQuantity:
    """Represents a quantity with mean value, lower and upper bounds 
    """
    
    def __init__(self, mean, bounds=None):
        if isinstance(mean, ureg.Quantity):
            self.mean = mean
        else:
            raise TypeError('mean should be a Quantity')
        if bounds is None:
            self.lower = self.mean.magnitude
            self.upper = self.mean.magnitude
        else:
            self.lower = min(min(bounds), self.mean.magnitude)
            self.upper = max(max(bounds), self.mean.magnitude)

    def as_list(self):
        return [self.lower, self.mean.magnitude, self.upper]
    
    def __copy__(self):
        return type(self)(copy.copy(self.mean),
                          copy.copy((self.lower, self.upper)))
    
    def __repr__(self):
        return "<BoundedQuantity({0} {1}, [{2} - {3}])>".format(self.mean.magnitude, self.mean.units, self.lower, self.upper)
    
    def __str__(self):
        return "{0:.3f} {1:.3f}, [{2:.3f} ; {3:.3f}]".format(self.mean.magnitude, self.mean.units,
                                             self.lower, self.upper)
    
    def __eq__(self, other):
        if isinstance(other, type(self)):
            return (self.mean == other.mean
                    and self.lower == other.lower
                    and self.upper == other.upper) 
        else:
            return False
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    @property
    def mean(self):
        return self._mean
    
    @property
    def lower(self):
        return self._lower
    
    @property
    def upper(self):
        return self._upper
    
    @property
    def units(self):
        return self.mean.units
    
    @staticmethod
    def get_magnitude(obj):
        if isinstance(obj, ureg.Quantity):
            return obj.magnitude
        elif isinstance(obj, Number):
            return obj
        else:
            raise TypeError("object should be a Number or Quantity")
    
    @mean.setter
    def mean(self, quantity):
        self._mean = quantity
    
    @lower.setter
    def lower(self, val):
        self._lower = min(self.get_magnitude(val), self.mean.magnitude)
    
    @upper.setter
    def upper(self, val):
        self._upper = max(self.get_magnitude(val), self.mean.magnitude)
    
    def _iop(self, other, op):
        """Perform in-place operation and return the result
        
        :param other: argument of the operator function
        :type other: BoundedQuantity, Quantity or numeric type
        :param op: operator function, (e.g. operator.sub)
        """
        if isinstance(other, BoundedQuantity):
            other_m = other.mean
            other_l = other.lower
            other_u = other.upper
        elif isinstance(other, ureg.Quantity):
            other_m = other
            other_l = other.magnitude
            other_u = other.magnitude
        elif isinstance(other, Number):
            other_m = other
            other_l = other
            other_u = other
        else:
            raise TypeError("unsupported type: {}".format(type(other)))
        self.mean = op(self.mean, other_m)
        bounds = (op(self.upper, other_l),
                  op(self.lower, other_u),
                  op(self.upper, other_u),
                  op(self.lower, other_l))
        self.lower = min(bounds)
        self.upper = max(bounds)
        
        return self
    
    def _op(self, other, op):
        """Perform operation and return the result
        
        :param other: argument of the operator function
        :type other: BoundedQuantity, Quantity or numeric type
        :param op: operator function, (e.g. operator.add)
        """
        return self.__copy__()._iop(other, op)
    
    def __add__(self, other):
        return self._op(other, operator.add)
    
    def __iadd__(self, other):
        return self._iop(other, operator.add)
    
    __radd__ = __add__
    
    def __sub__(self, other):
        return self._op(other, operator.sub)
    
    def __isub__(self, other):
        return self._iop(other, operator.sub)
    
    def __rsub__(self, other):
        return -self.__sub__(other)
    
    def __mul__(self, other):
        return self._op(other, operator.mul)
    
    def __imul__(self, other):
        return self._iop(other, operator.mul)
    
    __rmul__ = __mul__
    
    def __truediv__(self, other):
        return self._op(other, operator.truediv)
    
    def __itruediv__(self, other):
        return self._iop(other, operator.truediv)
    
    def __rtruediv__(self, other):
        return self.__truediv__(other)**(-1)
    
    def __pow__(self, other):
        if isinstance(other, Number):
                return self._op(other, operator.pow)
    
    def __ipow__(self, other):
        if isinstance(other, Number):
            return self._iop(other, operator.pow)
    
    def __abs__(self):
        return type(self)(abs(self.mean), (abs(self.lower), abs(self.upper)))
    
    def __neg__(self):
        return type(self)(-self, (-self.upper, -self.lower))
    
    def ito(self, units):
        """Inplace rescale to different units.

        :param other: destination units.
        :type other: Quantity, str or dict
        """
        old_units = self.mean.units
        bounds = ((self.lower * old_units).to(units).magnitude,
                  (self.upper * old_units).to(units).magnitude)
        self.mean.ito(units)
        self.lower = min(bounds)
        self.upper = max(bounds)
        return self
    
    def to(self, units):
        """Return rescale to different units.

        :param other: destination units.
        :type other: Quantity, str or dict
        """
        return self.__copy__().ito(units)





















