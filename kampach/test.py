import unittest

from . import ureg
from .arithmetic import BoundedQuantity as BQ_, parse_quantity
from .geometry import TruncatedPyramid, Cuboid, Superstructure, Prism,\
    Stairs
from .site import Site, Building, TransportActivity, ProductionActivity
from .valuable import LinearQuantitativeValuableInput as LQVI
from .xmlio import create_object_from_xml_element, save_xml_file,\
    load_xml_file
import xml.etree.ElementTree as ET

m = 1*ureg.meter
m2 = m*m
m3 = m*m*m
kg = 1*ureg.kilogram
wd = 1*ureg.work_day
kph = 1*ureg.kph
l = 1*ureg.liter


class TestArithmetic(unittest.TestCase):
    
    def test_bounds(self):
        bq1 = BQ_(3*m)
        bq2 = BQ_(3*m, (3, 3))
        self.assertEqual(bq1, bq2)
        bq2.lower = 4
        bq2.upper = 0
        self.assertEqual(bq1, bq2)
    
    def test_op(self):
        bq1 = BQ_(2*m, (1, 5))
        bq2 = BQ_(3*m, (2, 4))
        bqsum = BQ_(5.*m, (3., 9.))
        bqdif = BQ_(1.*m, (-3., 3.))
        bqmul = BQ_(6.*m**2, (2., 20.))
        self.assertEqual(bq2+bq1, bqsum)
        self.assertEqual(bq2-bq1, bqdif)
        self.assertEqual(bq2*bq1, bqmul)
        self.assertEqual(bq1, bq1+0)
        self.assertEqual(bq1, bq1*(1*m)/(1*m))
    
    def test_mutable(self):
        bq1 = BQ_(2*m, (1, 5))
        bq2 = bq1
        self.assertTrue(bq2 is bq1)
        bq2 *= 3
        self.assertTrue(bq2 is bq1)
    
    def test_rescale(self):
        bqm = BQ_(0.9144*m)
        bqy = bqm.to(ureg.yard)
        self.assertEqual(bqy.mean.magnitude, 1)
        self.assertEqual(bqy.lower, 1)
        self.assertEqual(bqy.upper, 1)
    
    def test_bounded_mul_classical(self):
        bq = BQ_(1*m, (0.9, 1.1))
        q = 2*m
        self.assertIsInstance(bq*q, BQ_)
        self.assertIsInstance(q*bq, BQ_)
        self.assertIsInstance((bq*q)*q, BQ_)
        self.assertIsInstance(bq*(q*q), BQ_)
        self.assertIsInstance((q*bq)*q, BQ_)
        self.assertIsInstance(q*(bq*q), BQ_)
        self.assertIsInstance((q*q)*bq, BQ_)
        self.assertIsInstance(q*(q*bq), BQ_)

    def test_parse_quantity(self):
        bq1 = BQ_(1*m, (0.9, 1.1))
        bq2 = parse_quantity(str(bq1))
        self.assertEqual(bq1, bq2)

class TestValuable(unittest.TestCase):
    
    def test_compute_cost_overload(self):
        pass
#         v = LinearQuantitativeValuable(amount=11)
#         v1 = LinearQuantitativeValuable(marginal_cost=2.)
#         v2 = LinearQuantitativeValuable(marginal_cost=1.5)
#         v.append_input(LinearQuantitativeValuableInput(valuable=v1, marginal_amount=2.))
#         v.append_input(LinearQuantitativeValuableInput(valuable=v2, marginal_amount=5.))
#         print( v.compute_total_cost())


class TestXML(unittest.TestCase):
    
    def test_create(self):
        elem = ET.Element('Site')
        elem.set('name', 'My site')
        obj = create_object_from_xml_element(elem)
        self.assertIsInstance(obj, Site)
        self.assertTrue(hasattr(obj, 'name'))
        self.assertEqual(obj.name, 'My site')
    
    def test_bad_xml(self):
        with self.assertRaises(ValueError):
            elem = ET.Element('BadTag')
            create_object_from_xml_element(elem)

class TestSite(unittest.TestCase):
    
    def test_full_site(self):
        # Create an archeological site
        site = Site('A first archeological site')
        
        sup = Building('A superstructure')
        site.inputs.append(sup)
        sup.shape = Superstructure(finish_thickness=BQ_(0.25*m),
                                   number_of_rooms=2,
                                   depth=BQ_(4*m), width=BQ_(7*m),
                                   walls_thickness=BQ_(0.6*m),
                                   door_width=BQ_(0.8*m),
                                   door_height=BQ_(1.5*m),
                                   ceiling_height=BQ_(3*m),
                                   outer_height=BQ_(4.5*m))
        
        # Create a building
        building = Building('A first building')
        
        # Here we say that the building belong to the site
        site.inputs.append(building)
        
        # Create the building's geometry
        
        # The shape of the building is a truncated pyramid
        building.shape = TruncatedPyramid(finish_thickness=BQ_(0.5*m),
                                          bottom_length=BQ_(30*m),
                                          bottom_width=BQ_(20*m),
                                          top_length=BQ_(10*m),
                                          top_width=BQ_(5*m),
                                          height=BQ_(10*m))
        
        # Create a cuboid inside the building (this will subtract the
        # total volume of the cuboid from the fill volume of the building)
        cuboid = Cuboid(length=BQ_(5*m), width=BQ_(5*m), height=BQ_(5*m))
        building.substructures.append(cuboid)
        
        # Also create a prism
        prism = Prism(finish_thickness=BQ_(0.5*m), width=BQ_(5*m), depth=BQ_(5*m), height=BQ_(5*m))
        building.substructures.append(prism)
        
        # Now we define the activities needed to fill the volumes and areas.
        
        # Activities of the first building
        
        # Fill volume
        
        # Create earth packing activity
        earth_packing = ProductionActivity('Earth packing')
        
        # Set a linear dependance between the target (the fill volume) and the
        # input (the packed earth) (LQVI stands for LinearQuantitativeValuableInput)
        building.inputs.append(LQVI(target_valuable=building,
                                    input_valuable=earth_packing,
                                    target_amount='fill_volume',
                                    marginal_amount=BQ_(1000*kg/m3),
                                    fixed_amount=0))
        
        # Set the cost of the  activity
        earth_packing.marginal_cost = BQ_(2000*wd/kg)
        
        # Create earth transporting activity as input for earth packing
        earth_transporting = TransportActivity(name='Earth transporting',
                                               amount_per_travel=BQ_(50*kg),
                                               speed_loaded=BQ_(2*kph),
                                               speed_empty=BQ_(5*kph),
                                               distance=BQ_(100*m))
        
        # Set the linear dependance between the amount of packed earth and the amount
        # of transported earth (assuming there is no loss, the marginal amount is 1)
        earth_packing.inputs.append(LQVI(target_valuable=earth_packing,
                                         input_valuable=earth_transporting,
                                         marginal_amount=1.))
        
        # And so on, for the finish volume and area
        wall_building = ProductionActivity('Wall building')
        building.inputs.append(LQVI(target_valuable=building,
                                    input_valuable=wall_building,
                                    target_amount='finish_volume',
                                    marginal_amount=BQ_(2000*kg/m3)))
        wall_building.marginal_cost = BQ_(1000*wd/kg)
        
        plaster_laying = ProductionActivity('Plaster laying')
        building.inputs.append(LQVI(target_valuable=building,
                                    input_valuable=plaster_laying,
                                    target_amount='total_finish_area',
                                    marginal_amount=BQ_(10*l/m2)))
        plaster_laying.marginal_cost = BQ_(0.1*wd/l)
        
        stairs_building = Building('Stairs')
        stairs_building.shape = Stairs(finish_thickness=0.5*m, bottom_length=3*m,
                                       bottom_width=3*m, top_length=2*m,
                                       top_width=0.5*m, height=9*m, depth=4*m)
        site.inputs.append(stairs_building)
        
        print("Total cost: {}".format(site.compute_total_cost()))
        
        save_xml_file(site, "tests/Site.xml")
        
        site_loaded = load_xml_file("tests/Site.xml")
        save_xml_file(site_loaded, "tests/Site_reloaded.xml")


class TestGeometry(unittest.TestCase):
    
    def test_truncated_pyramid_pointy(self):
        pyr = TruncatedPyramid(0, 6., 6., 0., 0., 4.)
        walls_area = pyr.compute_walls_finish_area()
        top_area = pyr.compute_top_finish_area()
        vol = pyr.compute_total_volume()
        self.assertEqual(walls_area, 60.)
        self.assertEqual(top_area, 0.)
        self.assertEqual(vol, 48.)
    
    def test_cuboid(self):
        cub = Cuboid(0, 2., 3., 5.)
        walls_area = cub.compute_walls_finish_area()
        top_area = cub.compute_top_finish_area()
        vol = cub.compute_total_volume()
        self.assertEqual(walls_area, 50.)
        self.assertEqual(top_area, 6.)
        self.assertEqual(vol, 30.)
    
    @staticmethod
    def print_shape_data(shape):
        print(type(shape).__name__)
        print('   total volume: {}'.format(shape.compute_total_volume()))
        print('   fill volume: {}'.format(shape.compute_fill_volume()))
        print('   finish volume: {}'.format(shape.compute_finish_volume()))
        print('   walls area: {}'.format(shape.compute_walls_finish_area()))
        print('   top area: {}'.format(shape.compute_top_finish_area()))
        print('   total area: {}'.format(shape.compute_total_finish_area()))
    
    def test_stairs(self):
        stairs = Stairs(finish_thickness=0.5*m, bottom_length=3*m,
                        bottom_width=3*m, top_length=2*m,
                        top_width=0.5*m, height=9*m, depth=4*m)
        self.print_shape_data(stairs)
    
    def test_superstructure(self):
        sup = Superstructure(finish_thickness=0.25*m, number_of_rooms=2,
                             depth=4*m, width=7*m, walls_thickness=0.6*m,
                             door_width=0.8*m, door_height=1.5*m, ceiling_height=3*m,
                             outer_height=4.5*m)
        self.print_shape_data(sup)
    
    def test_truncated_pyramid_cube_bounded_quantities(self):
        one = BQ_(1*m)
        pyr = TruncatedPyramid(0, one, one, one, one, one)
        walls_area = pyr.compute_walls_finish_area()
        vol = pyr.compute_total_volume()
        self.assertEqual(walls_area, BQ_(4.*m**2))
        self.assertEqual(vol, BQ_(1.*m**3))
