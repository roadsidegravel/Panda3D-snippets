from direct.gui.DirectGui import *
import direct.gui.DirectGuiGlobals as DGG
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from math import pi as PI

class MyGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        base.setFrameRateMeter(True)
        self.set_up_camera()
        self.set_up_collision_handling()  
        self.create_menu()
        self.randomizer = Randomizer(0)    
        self.totalNeedles = 0
        self.touchingNeedles = 0
        self.amountOfNeedles = 1000
        self.needleHolder = render.attachNewNode('needleHolder')       
        
    def create_menu(self):
        self.menuHolder = DirectFrame(
                parent = aspect2d,
                frameSize = (-0.91, 0.91, -0.81, 0.81),
                relief = DGG.RAISED,
                borderWidth = (0.02, 0.02))
        self.explainationLabel = DirectLabel(
                parent = self.menuHolder,
                text = 'Guesstimate pi by dropping needles onto evenly spaced lines.',
                pos = (0, 0, 0.74),
                scale = 0.063)
        self.buffonsLabel = DirectLabel(
                parent = self.menuHolder,
                text = "A side effect of Buffon's needle problem.",
                pos = (0, 0, 0.66),
                scale = 0.063)
        self.thicknessLabel = DirectLabel(
                parent = self.menuHolder,
                text = "Distance between the lines: 3.00",
                pos = (0, 0, 0.45),
                scale = 0.063)
        self.thicknessSlider = DirectSlider(
                parent = self.menuHolder,
                range = (1.00, 5.00),
                value = 3.00,
                pageSize = 0.2,
                pos = (0, 0, 0.40),
                scale = 0.5, 
                command = self.cmd_thicknessSlider)
        self.thicknessMinLabel = DirectLabel(
                parent = self.menuHolder,
                text = "1.00",
                pos = (-0.575, 0, 0.3878),
                scale = 0.063)
        self.thicknessMaxLabel = DirectLabel(
                parent = self.menuHolder,
                text = "5.00",
                pos = (0.575, 0, 0.3878),
                scale = 0.063)
        self.shorterLabel = DirectLabel(
                parent = self.menuHolder,
                text = "The needle must be equal to or shorter than the line distance.",
                pos = (0, 0, 0.25),
                scale = 0.063)
        self.needleLabel = DirectLabel(
                parent = self.menuHolder,
                text = "Needle length: 3.00 (100%)",
                pos = (0, 0, 0.17),
                scale = 0.063)
        self.needleLengthSlider = DirectSlider(
                parent = self.menuHolder,
                range = (0.1, 1.0),
                value = 1,
                pageSize = 0.1,
                pos = (0, 0, 0.12),
                scale = 0.5,
                command = self.cmd_needleLengthSlider)
        self.needleMinLabel = DirectLabel(
                parent = self.menuHolder,
                text = "10%",
                pos = (-0.57, 0, 0.11),
                scale = 0.063)
        self.needleMaxLabel = DirectLabel(
                parent = self.menuHolder,
                text = "100%",
                pos = (0.575, 0, 0.11),
                scale = 0.063)
        self.startButton = DirectButton(
                parent = self.menuHolder,
                text = 'start',
                pos = (0, 0, -0.5),
                scale = 0.1,
                frameColor = (0.8, 0.95, 0.8, 1),
                command = self.cmd_start)
    
    def create_interface(self):
        font = loader.loadFont('Assets/FontsFree-Net-SLC_.ttf')
        self.textCount = OnscreenText(
                text = 'needles thrown: 0',
                pos = (0.99, 0.95),
                scale = 0.05,
                align = TextNode.ARight,
                font = font,
                mayChange = True)
        self.textPiGuess = OnscreenText(
                text = 'guesstimate: /',
                pos = (0.99, 0.9),
                scale = 0.05,
                align = TextNode.ARight,
                font = font,
                mayChange = True)
        self.textPi = OnscreenText(
                text = f'pi: {round(PI,5)}',
                pos = (0.99, 0.85),
                align = TextNode.ARight,
                font = font,
                scale = 0.05)
        
        
    def cmd_needleLengthSlider(self):
        thickValue = self.thickness
        needleValue = self.needleLengthSlider['value']
        percent = round(needleValue * 100)
        length = round(percent/100 * thickValue, 2)
        needleString = f"Needle length: {length} ({percent}%)"
        self.needleLabel['text'] = needleString
        self.length = length
        
    def cmd_start(self):
        windowWidth = self.win.get_properties().size.x
        distance = 20 * self.thickness
        self.amountOfLines = int(windowWidth/distance) + 1
        self.place_lines(self.thickness, self.amountOfLines)
        self.menuHolder.hide()
        self.create_interface()
        self.start_task_drop_needles()        
        
    def cmd_thicknessSlider(self):
        thickValue = round(self.thicknessSlider['value'], 1)
        thickString = f"Distance between the lines: {thickValue}"
        self.thicknessLabel['text'] = thickString
        self.thickness = thickValue
        self.cmd_needleLengthSlider()        
    
    def set_up_collision_handling(self):
        self.colTraverser = CollisionTraverser('traverser')
        self.colHandler = CollisionHandlerQueue()
        
    def set_up_camera(self):
        base.disableMouse() # disables default mouse control camera
        base.camera.setPos(0, 0, 20)
        base.camera.lookAt(0, 0, 0)
        lens = OrthographicLens()
        lens.setFilmSize(20, 15)
        base.cam.node().setLens(lens)
        
    def start_task_drop_needles(self):
        taskMgr.add(self.task_drop_needles, 'drop needles', extraArgs = [self.amountOfNeedles], appendTask = True)

    def place_lines(self, distance, amount):
        for a in range(amount):
            line = render.attachNewNode(CollisionNode('line'))
            pointA = Point3(0, -10, 2)
            pointB = Point3(0, -10, -2)
            pointC = Point3(0, 10,  -2)
            pointD = Point3(0, 10, 2)
            collisionSolid = CollisionPolygon(pointA, pointB, pointC, pointD)
            line.node().addSolid(collisionSolid)
            line.setPos((amount/2 - a) * distance, 0, 0)
            line.setCollideMask(BitMask32(1))
            line.node().setFromCollideMask(BitMask32().all_off())
            line.show()
            
    def place_needle(self, length):
        self.totalNeedles += 1
        newNeedle = self.needleHolder.attachNewNode(CollisionNode('needle'))
        collisionSegment = CollisionSegment(-length/2, 0, 0, length/2, 0, 0)
        newNeedle.node().addSolid(collisionSegment)
        newNeedle.show()
        t = self.thickness
        x = self.randomizer.random_real(t*5) - t*2.5
        y = self.randomizer.random_real(t*3) - t*1.5
        z = 0
        h = self.randomizer.random_real(360)
        newNeedle.setPos(x, y, z)
        newNeedle.setH(h)
        newNeedle.setCollideMask(BitMask32().all_off())
        newNeedle.node().setFromCollideMask(BitMask32(1))
        self.colTraverser.add_collider(newNeedle, self.colHandler)
    
    def task_drop_needles(self, amountOfNeedles, task):
        for n in range(amountOfNeedles):
            self.place_needle(self.length)
        taskMgr.add(self.task_count_needles, 'count needles')
        return task.done
    
    def task_count_needles(self, task):
        self.colTraverser.traverse(render)
        self.touchingNeedles += len(self.colHandler.entries)
        self.guesstimate_pi()
        taskMgr.doMethodLater(0.2, self.task_remove_dropped_needles, 'remove needles')
        return task.done
    
    def task_remove_dropped_needles(self, task):
        for needle in self.needleHolder.getChildren():
            needle.removeNode()
        self.colTraverser.clearColliders()
        self.start_task_drop_needles()
        return task.done
    
    def guesstimate_pi(self):
        numerator = 2 * self.length * self.totalNeedles
        denominator = self.thickness * self.touchingNeedles
        piApprox = numerator/denominator
        self.randomizer = Randomizer(0)
        countString = f'needles thrown: {self.totalNeedles}'
        self.textCount.setText(countString)
        guesstimateString = f'guesstimate: {round(piApprox,5)}'
        self.textPiGuess.setText(guesstimateString)        
        
app = MyGame()
app.run()
