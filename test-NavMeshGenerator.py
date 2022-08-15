# https://www.tutorialspoint.com/unittest_framework/unittest_framework_test_discovery.htm
# For example, in order to discover the tests in modules whose names start with 'assert' in 'tests' directory, the following command line is used −
# C:\python27>python –m unittest –v –s "c:\test" –p "assert*.py"
# --verbose -v
# --start-discovery -s
# --pattern -p
# --top-level-directory -t (defaults to start directory)

import csv # can switch to pandas or other if the need arises
import unittest

from panda3d.core import *

from NavMeshGenerator import NavMeshGenerator

class TestNavMeshGeneratorDefaultValues(unittest.TestCase):
    def setUp(self):
        self.navMeshGenerator = NavMeshGenerator()
        # delete default navmesh if it exists
        defaultFileName = self.navMeshGenerator.filepath
        defaultFileName.unlink()        
         
    
    def test_default_navmesh_exists_after_generating(self):
        defaultMeshPath = self.navMeshGenerator.filepath
        self.navMeshGenerator.generate()
        self.assertTrue(defaultMeshPath.exists())
        
    def test_default_navmesh_length_check(self):
        defaultMeshPath = self.navMeshGenerator.filepath
        desired = self.navMeshGenerator.gridSize ** 2 * 9 + 2
        self.navMeshGenerator.generate()
        linecounter = 0
        with open(defaultMeshPath) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                linecounter += 1
        self.assertEqual(linecounter, desired)
        
    def test_default_navmesh_first_line_check(self):
        defaultMeshPath = self.navMeshGenerator.filepath
        desired = ['Grid Size', str(self.navMeshGenerator.gridSize)]
        self.navMeshGenerator.generate()
        with open(defaultMeshPath) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            firstline = next(reader).copy()
        self.assertEqual(desired, firstline)
        
    def test_default_navmesh_second_line_check(self):
        defaultMeshPath = self.navMeshGenerator.filepath
        desired = ['NULL', 'NodeType', 'GridX', 'GridY', 'Length', 'Width', 'Height', 'PosX', 'PosY', 'PosZ']
        self.navMeshGenerator.generate()
        with open(defaultMeshPath) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            firstline = next(reader).copy()
            secondline = next(reader).copy()
        self.assertEqual(desired, secondline)
        
    def test_default_navmesh_last_nine_lines_check(self):
        defaultMeshPath = self.navMeshGenerator.filepath
        desired = [['0', '0', '9', '9', '5', '5', '0', '45.0', '45.0', '0.0'],
                   ['1', '1', '0', '0', '0', '0', '0', '0', '0', '0'],
                   ['0', '1', '8', '9', '5', '5', '0', '40.0', '45.0', '0.0'],
                   ['0', '1', '8', '8', '5', '5', '0', '40.0', '40.0', '0.0'],
                   ['0', '1', '9', '8', '5', '5', '0', '45.0', '40.0', '0.0'],
                   ['1', '1', '0', '0', '0', '0', '0', '0', '0', '0'],
                   ['1', '1', '0', '0', '0', '0', '0', '0', '0', '0'],
                   ['1', '1', '0', '0', '0', '0', '0', '0', '0', '0'],
                   ['1', '1', '0', '0', '0', '0', '0', '0', '0', '0']]
        
        self.navMeshGenerator.generate()
        with open(defaultMeshPath) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            rows = []
            lastNine = list(reader)[-9::]
        self.assertEqual(desired, lastNine, '\n\nThis was hardcoded and will be wrong if default values change')
        
    def test_default_navmeshgenerator_mask_all_zeroes(self):
        mask = self.navMeshGenerator.bitMask
        desired = ' 0000 0000 0000 0000 0000 0000 0000 0000\n'
        self.assertEqual(desired, str(mask))
        
class TestNavMeshGeneratorCollisions(unittest.TestCase):
    def setUp(self):
        self.navMeshGenerator = NavMeshGenerator()
        # delete default navmesh if it exists
        defaultFileName = self.navMeshGenerator.filepath
        defaultFileName.unlink()
        
    def tearDown(self):
        # delete navmesh if we made one
        fileName = self.navMeshGenerator.filepath
        fileName.unlink()
                
    def test_mask_but_no_collisions(self):
        self.navMeshGenerator.bitMask = BitMask32(0x12)
        self.navMeshGenerator.dirname = 'NavMeshes'
        self.navMeshGenerator.basename = 'obstaclenavmesh.csv'
        basePath = NodePath('basenode')
        self.navMeshGenerator.scene = basePath
        meshPath = self.navMeshGenerator.filepath
        self.navMeshGenerator.generate()
        with open(meshPath) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            result = len(list(reader))
        basePath.removeNode()
        desired = self.navMeshGenerator.gridSize**2*9+2
        self.assertEqual(desired, result)
        
    def test_mask_with_collisions(self):
        colMask = BitMask32(0x12)
        self.navMeshGenerator.bitMask = colMask
        self.navMeshGenerator.dirname = 'NavMeshes'
        self.navMeshGenerator.basename = 'obstaclenavmesh.csv'
        basePath = NodePath('basenode')
        self.navMeshGenerator.scene = basePath
        cs = CollisionSphere(0, 0, 0, self.navMeshGenerator.gridSize)
        csPath = basePath.attachNewNode(CollisionNode('cs'))
        csPath.node().addSolid(cs)
        csPath.setX(self.navMeshGenerator.bottomLeftCorner.x + self.navMeshGenerator.xstep * self.navMeshGenerator.gridSize/2)
        csPath.setY(self.navMeshGenerator.bottomLeftCorner.y + self.navMeshGenerator.ystep * self.navMeshGenerator.gridSize/2)
        meshPath = self.navMeshGenerator.filepath
        self.navMeshGenerator.generate()
        with open(meshPath) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            result = len(list(reader))
        basePath.removeNode()
        complete = self.navMeshGenerator.gridSize**2*9+2
        self.assertTrue(complete > result)  


if __name__ == '__main__':
    unittest.main()