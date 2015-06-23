
import unittest2
import numpy as np
from grid_cell_model.analysis.image import Position2D
from grid_cell_model.analysis.geometry import min_dist_to_line, bounding_box, bounding_box_dimensions
from grid_cell_model.analysis.geometry import bounding_box_dimensions, scaleLine
from math import sqrt


notImplMsg = "Not implemented"


##############################################################################


class Test_Geometry(unittest2.TestCase):
    
    def assertApproxEqual(self, first, second, accuracy, msg=None):
        #print first, second
        np.testing.assert_almost_equal(first, second, accuracy)

    def setUp(self):
        pass
        #self.addTypeEqualityFunc(float, self.assertApproxEqual)

    def test_min_dist_to_line(self):

	accuracy = 7
	
        # test 1
        l = Position2D(0.0, 4.0), Position2D(4.0, 0.0)
        p = Position2D(4.0, 4.0)
        self.assertApproxEqual(min_dist_to_line(p, l), sqrt(2 * (4 ** 2))/2, accuracy)

        # test 2
        l = Position2D(0.0, 4.0), Position2D(4.0, 0.0)
        p = Position2D(-4.0, -4.0)
        self.assertApproxEqual(min_dist_to_line(p, l), sqrt(2 * (4 ** 2))*3/2, accuracy)

	accuracy = 1

        # test 3
        l = Position2D(3.5, 1.5), Position2D(-3.5, 5.5)
        p = Position2D(2.0, 5.0)
        self.assertApproxEqual(min_dist_to_line(p, l), 2.3, accuracy)

        # test 4
        l = Position2D(3.5, 1.5), Position2D(-3.5, 5.5)
        p = Position2D(5.5, 2.0)
        self.assertApproxEqual(min_dist_to_line(p, l), 2.1, accuracy)

        # test 5
        l = Position2D(0.0, 4.0), Position2D(4.0, 0.0)
        p = Position2D(0.0, 4.0)
        self.assertApproxEqual(min_dist_to_line(p, l), 0.0, accuracy)
    

    def test_bounding_box(self):
        
        # test 1 - rectangle
        shape = [Position2D(-4.0, 4.0), Position2D(4.0, 4.0), 
                 Position2D(4.0, -4.0), Position2D(-4.0, -4.0) ]
	expected = Position2D(-4.0, 4.0), Position2D(4.0, -4.0)
        actual = bounding_box(shape)
        self.assertEqual(actual[0].x, expected[0].x)
        self.assertEqual(actual[0].y, expected[0].y)
        self.assertEqual(actual[1].x, expected[1].x)
        self.assertEqual(actual[1].y, expected[1].y)

        # test 2 - diamond
        shape = [Position2D(0.0, 4.0), Position2D(4.0, 0.0), 
                 Position2D(0.0, -4.0), Position2D(-4.0, -0.0) ]
	expected = Position2D(-4.0, 4.0), Position2D(4.0, -4.0)
        actual = bounding_box(shape)
        self.assertEqual(actual[0].x, expected[0].x)
        self.assertEqual(actual[0].y, expected[0].y)
        self.assertEqual(actual[1].x, expected[1].x)
        self.assertEqual(actual[1].y, expected[1].y)

    def test_bounding_box_dimensions(self):
        
        # test 1 - rectangle
        shape = [Position2D(-4.0, 4.0), Position2D(4.0, 4.0), 
                 Position2D(4.0, -4.0), Position2D(-4.0, -4.0) ]
	expected = 8.0, 8.0
        actual = bounding_box_dimensions(shape)
        self.assertTupleEqual(expected, actual)

        # test 2 - diamond
        shape = [Position2D(0.0, 10.0), Position2D(5.0, 0.0), 
                 Position2D(0.0, -10.0), Position2D(-5.0, 0.0) ]
	expected = 10.0, 20.0
        actual = bounding_box_dimensions(shape)
        self.assertTupleEqual(expected, actual)

    def test_scale_line(self):
        
        # test 1 - diagonal downslope
        originalLine = Position2D(0.0, 100.0), Position2D(100.0, 0.0)
        originalDim = 100.0, 100.0
	newDim = 10.0, 10.0
        expected = Position2D(0.0, 10.0), Position2D(10.0, 0.0)
        actual = scaleLine(originalLine, originalDim, newDim)
        self.assertEqual(actual[0].x, expected[0].x)
        self.assertEqual(actual[0].y, expected[0].y)
        self.assertEqual(actual[1].x, expected[1].x)
        self.assertEqual(actual[1].y, expected[1].y)

        # test 2 - diagonal upslope
        originalLine = Position2D(-50.0, -50.0), Position2D(50.0, 50.0)
        originalDim = 50.0, 50.0
	newDim = 5.0, 5.0
        expected = Position2D(-5.0, -5.0), Position2D(5.0, 5.0)
        actual = scaleLine(originalLine, originalDim, newDim)
        self.assertEqual(actual[0].x, expected[0].x)
        self.assertEqual(actual[0].y, expected[0].y)
        self.assertEqual(actual[1].x, expected[1].x)
        self.assertEqual(actual[1].y, expected[1].y)

        # test 3 - vertical line
        originalLine = Position2D(-50.0, -50.0), Position2D(-50.0, 50.0)
        originalDim = 100.0, 100.0
	newDim = 50.0, 50.0
        expected = Position2D(-25.0, -25.0), Position2D(-25.0, 25.0)
        actual = scaleLine(originalLine, originalDim, newDim)
        self.assertEqual(actual[0].x, expected[0].x)
        self.assertEqual(actual[0].y, expected[0].y)
        self.assertEqual(actual[1].x, expected[1].x)
        self.assertEqual(actual[1].y, expected[1].y)

        # test 4 - horizontal line
        originalLine = Position2D(-50.0, -50.0), Position2D(50.0, -50.0)
        originalDim = 100.0, 100.0
	newDim = 50.0, 50.0
        expected = Position2D(-25.0, -25.0), Position2D(25.0, -25.0)
        actual = scaleLine(originalLine, originalDim, newDim)
        self.assertEqual(actual[0].x, expected[0].x)
        self.assertEqual(actual[0].y, expected[0].y)
        self.assertEqual(actual[1].x, expected[1].x)
        self.assertEqual(actual[1].y, expected[1].y)

if __name__ == '__main__':   
    unittest2.main()


