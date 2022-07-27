from direct.showbase.ShowBase import ShowBase
from panda3d.core import *


class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.maskNone = BitMask32(0)
        self.maskPicker = BitMask32(0x30)
        
        self.disableMouse()
        self.camera.setPos(0, -10, 10)
        self.camera.setHpr(0, -45, 0)
        
        self.pickerHandler = CollisionHandlerQueue()
        self.pickerTraverser = CollisionTraverser('pickerTraverser')        
        pickerNode = CollisionNode('pickerRay')
        pickerNP = base.cam.attachNewNode(pickerNode)
        pickerNode.setFromCollideMask(self.maskPicker)
        pickerNode.setIntoCollideMask(self.maskNone)
        self.pickerRay = CollisionRay()
        pickerNode.addSolid(self.pickerRay)
        self.pickerTraverser.addCollider(pickerNP, self.pickerHandler)       
        
        self.tileMarker = render.attachNewNode('tile marker')
        self.tileMarker.setColor(0.8, 0.8, 0.8, 1)
        tileMarkerModel = loader.loadModel('Assets\square.egg')
        tileMarkerModel.setHpr(270, 270, 0)
        tileMarkerModel.reparentTo(self.tileMarker)
        tileMarkerModel.setColor(0.5, 0.8, 0.5, 0.25)
        tileMarkerModel.setTransparency(TransparencyAttrib.MAlpha)        
        
        plane = CollisionPlane(Plane(Vec3(0, 0, 1), Point3(0, 0, 0))) #normal and point constructor
        pickerPlane = render.attachNewNode(CollisionNode('cnode'))
        pickerPlane.node().addSolid(plane)
        pickerPlane.node().setIntoCollideMask(self.maskPicker)
        # sceneColPlaneNP.show()
        
        taskMgr.add(self.task_move_tile_marker, 'move tile marker')


    def task_move_tile_marker(self, task):            
        if self.tileMarker is not None:
            if base.mouseWatcherNode.hasMouse():
                mousePos = base.mouseWatcherNode.getMouse()
                self.pickerRay.setFromLens(base.camNode, mousePos.x, mousePos.y)
                self.pickerTraverser.traverse(render)
                self.pickerHandler.sortEntries()
                colPos = self.pickerHandler.getEntry(0).getSurfacePoint(render)
                # square grids
                #   round(x)  ->  0, 1, 2,...
                #   round(x * 2) / 2  ->  for 0, 0.5, 1, 1.5, 2,...
                #   round(x)*2  -> 0, 2, 4, 6,...
                newx = round(colPos.x)
                newy = round(colPos.y)
                newz = round(colPos.z) 
                self.tileMarker.setPos(newx, newy, newz)           
        return task.cont
    
    
      
        
game = Game()
game.run()