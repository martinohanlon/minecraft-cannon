#www.stuffaboutcode.com
#Raspberry Pi, Minecraft Cannon

#import the minecraft.py module from the minecraft directory
import minecraft.minecraft as minecraft
#import minecraft block module
import minecraft.block as block
#import time, so delays can be used
import time
#import math, so we can use sin, cos and other maths functions
import math
#import cmd, so we can use the command line interpreter
import cmd

#Common functions
# compares vec3 objects, if they are the same returns true
def matchVec3(vec1, vec2):
    if ((vec1.x == vec2.x) and (vec1.y == vec2.y) and (vec1.z == vec2.z)):
        return True
    else:
        return False

# finds point on sphere (based on polar co-ordinates) 
def findPointOnSphere(cx, cy, cz, radius, phi, theta):
    #phi - angle around the pole 0<= phi <= 360
    #theta - angle from plan 'up' -90 <= theta <= 90
    x = cx + radius * math.cos(math.radians(theta)) * math.cos(math.radians(phi))
    z = cz + radius * math.cos(math.radians(theta)) * math.sin(math.radians(phi))
    y = cy + radius * math.sin(math.radians(theta))
    return int(round(x,0)), int(round(y,0)), int(round(z,0))

#Class to handle minecraft drawing
class MinecraftDrawing:
    def __init__(self, mc):
        self.mc = mc

    # draw point
    def drawPoint3d(self, x, y, z, blockType, blockData=None):
        self.mc.setBlock(x,y,z,blockType,blockData)
        #print "x = " + str(x) + ", y = " + str(y) + ", z = " + str(z)

    # draws a sphere
    def drawSphere(self, vec3, radius, blockType, blockData=None):
    # if the diameter is greater than 1, create a sphere, ot
        if radius * 2.0 > 1.5:
            #round up radius
            radius = int(radius + 0.5)
            for x in range(radius*-1,radius):
                for y in range(radius*-1, radius):
                    for z in range(radius*-1,radius):
                        if x**2 + y**2 + z**2 < radius**2:
                            self.drawPoint3d(vec3.x + x, vec3.y + y, vec3.z + z, blockType, blockData)
        else:
            self.drawPoint3d(vec3.x, vec3.z, vec3.y, blockType, blockData)

    # draws a face, when passed a collection of vertices which make up a polyhedron
    def drawFace(self, vertices, blockType, blockData=None):
        
        # get the edges of the face
        edgesVertices = []
        # persist first vertex
        firstVertex = vertices[0]
        # loop through vertices and get edges
        vertexCount = 0
        for vertex in vertices:
            vertexCount+=1
            if vertexCount > 1:
                # got 2 vertices, get the points for the edge
                edgesVertices = edgesVertices + self.getLine(lastVertex.x, lastVertex.y, lastVertex.z, vertex.x, vertex.y, vertex.z)
            # persist the last vertex found    
            lastVertex = vertex
        # get edge between the last and first vertices
        edgesVertices = edgesVertices + self.getLine(lastVertex.x, lastVertex.y, lastVertex.z, firstVertex.x, firstVertex.y, firstVertex.z)

        # sort edges vertices
        def keyX( point ): return point.x
        def keyY( point ): return point.y
        def keyZ( point ): return point.z
        edgesVertices.sort( key=keyZ )
        edgesVertices.sort( key=keyY )
        edgesVertices.sort( key=keyX )

        # not very performant but wont have gaps between in complex models
        for vertex in edgesVertices:
            vertexCount+=1
            # got 2 vertices, draw lines between them
            if (vertexCount > 1):
                self.drawLine(lastVertex.x, lastVertex.y, lastVertex.z, vertex.x, vertex.y, vertex.z, blockType, blockData)
                #print "x = " + str(lastVertex.x) + ", y = " + str(lastVertex.y) + ", z = " + str(lastVertex.z) + " x2 = " + str(vertex.x) + ", y2 = " + str(vertex.y) + ", z2 = " + str(vertex.z)
            # persist the last vertex found
            lastVertex = vertex
        
    # draw's all the points in a collection of vertices with a block
    def drawVertices(self, vertices, blockType, blockData=None):
        for vertex in vertices:
            self.drawPoint3d(vertex.x, vertex.y, vertex.z, blockType, blockData)

    # draw line
    def drawLine(self, x1, y1, z1, x2, y2, z2, blockType, blockData=None):
        self.drawVertices(self.getLine(x1, y1, z1, x2, y2, z2), blockType, blockData)
    
    # returns points on a line
    def getLine(self, x1, y1, z1, x2, y2, z2):

        # return maximum of 2 values
        def MAX(a,b):
            if a > b: return a
            else: return b

        # return step
        def ZSGN(a):
            if a < 0: return -1
            elif a > 0: return 1
            elif a == 0: return 0

        # list for vertices
        vertices = []

        # if the 2 points are the same, return single vertice
        if (x1 == x2 and y1 == y2 and z1 == z2):
            vertices.append(minecraft.Vec3(x1, y1, z1))
                            
        # else get all points in edge
        else:
        
            dx = x2 - x1
            dy = y2 - y1
            dz = z2 - z1

            ax = abs(dx) << 1
            ay = abs(dy) << 1
            az = abs(dz) << 1

            sx = ZSGN(dx)
            sy = ZSGN(dy)
            sz = ZSGN(dz)

            x = x1
            y = y1
            z = z1

            # x dominant
            if (ax >= MAX(ay, az)):
                yd = ay - (ax >> 1)
                zd = az - (ax >> 1)
                loop = True
                while(loop):
                    vertices.append(minecraft.Vec3(x, y, z))
                    if (x == x2):
                        loop = False
                    if (yd >= 0):
                        y += sy
                        yd -= ax
                    if (zd >= 0):
                        z += sz
                        zd -= ax
                    x += sx
                    yd += ay
                    zd += az
            # y dominant
            elif (ay >= MAX(ax, az)):
                xd = ax - (ay >> 1)
                zd = az - (ay >> 1)
                loop = True
                while(loop):
                    vertices.append(minecraft.Vec3(x, y, z))
                    if (y == y2):
                        loop=False
                    if (xd >= 0):
                        x += sx
                        xd -= ay
                    if (zd >= 0):
                        z += sz
                        zd -= ay
                    y += sy
                    xd += ax
                    zd += az
            # z dominant
            elif(az >= MAX(ax, ay)):
                xd = ax - (az >> 1)
                yd = ay - (az >> 1)
                loop = True
                while(loop):
                    vertices.append(minecraft.Vec3(x, y, z))
                    if (z == z2):
                        loop=False
                    if (xd >= 0):
                        x += sx
                        xd -= az
                    if (yd >= 0):
                        y += sy
                        yd -= az
                    z += sz
                    xd += ax
                    yd += ay
                    
        return vertices

#Class for a bullet in Minecraft
class MinecraftBullet:
    def __init__(self, mc, startPos, direction, angle, velocity, blastRadius):
        
        #Value validation
        if direction < 0 or direction > 359:
            raise ValueError("direction must be an angle 0 - 359 degrees")
        if angle < 0 or angle > 90:
            raise ValueError("angle must be between 0 - 90 degrees")
        if velocity < 0 or velocity > 1:
            raise ValueError("velocity must be between 0 - 1 blocks per tick")

        #Gravity constant - its 'similar' to earth but different so stuff flies far but also stays inside the minecraft world!
        self.gravity = -0.0098

        #Properties
        self.mc = mc
        self.startPos = startPos
        self.currentPos = startPos
        self.direction = direction
        self.angle = angle
        self.velocity = velocity
        self.blastRadius = blastRadius
        self.ticks = 0

        #Minecraft Drawing Class
        self.mcDrawing = MinecraftDrawing(mc)

        #Calculate velocities in X and Z and Y based on direction and velocity
        # dont ask me how this works, I did it all on a bit of paper and Im not sure myself now!
        # y velocity will be re-calculated each time the bullet is updated to take gravity into account
        sinYVelocity = math.sin(math.radians(angle))
        self.yStartVelocity = velocity * sinYVelocity
        # work out horizontal direction in minecraft world, +/- in X,Z, taking into account velocity in Y
        self.xVelocity = (math.cos(math.radians(direction)) * velocity) * (1 - sinYVelocity)
        self.zVelocity = (math.sin(math.radians(direction)) * velocity) * (1 - sinYVelocity)

        #Draw the bullet
        self.drawPos = startPos
        self.draw()
        
    def draw(self):
        self.mcDrawing.drawPoint3d(self.drawPos.x, self.drawPos.y, self.drawPos.z, block.GLOWING_OBSIDIAN)

    def clear(self):
        self.mcDrawing.drawPoint3d(self.drawPos.x, self.drawPos.y, self.drawPos.z, block.AIR)

    def update(self):
        #Update the Bullet, should be called once per 'tick'
        # calculate new y velocity
        self.ticks += 1
        self.yVelocity = self.yStartVelocity + self.gravity * self.ticks
        
        # find the bullets new position
        newPos = minecraft.Vec3(self.currentPos.x + self.xVelocity,
                                self.startPos.y + (self.yStartVelocity * self.ticks + 0.5 * (self.gravity * pow(self.ticks,2))),
                                self.currentPos.z + self.zVelocity)
        #Has the bullet moved from its last drawn position
        # round the new position and compare it to the last drawn
        newDrawPos = minecraft.Vec3(int(round(newPos.x, 0)),
                                    int(round(newPos.y, 0)),
                                    int(round(newPos.z, 0)))
        movedBullet = True
        if matchVec3(newDrawPos, self.drawPos) == False:
            # if the bullet is moving to a block of air, move it, otherwise explode
            if self.mc.getBlock(newDrawPos.x, newDrawPos.y, newDrawPos.z) == block.AIR:
                # clear the last drawn bullet
                self.clear()
                # move the draw position
                self.drawPos = minecraft.Vec3(newDrawPos.x, newDrawPos.y, newDrawPos.z)
                # draw the bullet
                self.draw()
            else:
                #exploded
                self.mcDrawing.drawSphere(newDrawPos, self.blastRadius, block.AIR)
                movedBullet = False
        #Update the current position
        self.currentPos = newPos

        return movedBullet

#Class for a cannon in minecraft
class MinecraftCannon:
    def __init__(self, mc, position):
        
        #Constants
        self.lenghtOfGun = 5
        
        #Properties
        self.mc = mc
        self.position = position
        self.angle = 30
        self.direction = 0
        self.baseOfGun = minecraft.Vec3(position.x, position.y + 2, position.z)
        self.endOfGun = self.findEndOfGun()
        # minecraft drawing class
        self.mcDrawing = MinecraftDrawing(mc)
        # draw gun
        self.drawCannon()
        self.drawGun()

    def fire(self, velocity, blastRadius):
        #create new bullet
        bullet = MinecraftBullet(self.mc, self.endOfGun, self.direction, self.angle, velocity, blastRadius)
        return bullet

    def drawCannon(self):
        #mcDrawing = self.mcDrawing
        position = self.position
        self.mc.setBlocks(position.x - 1, position.y, position.z - 1,
                     position.x + 1, position.y + 1, position.z + 1,
                     block.WOOD_PLANKS)
        
    def clearCannon(self):
        position = self.position
        self.mc.setBlocks(position.x - 1, position.y, position.z - 1,
                     position.x + 1, position.y + 2, position.z + 1,
                     block.AIR)
        self.clearGun()

    def findEndOfGun(self):        
        x, y, z = findPointOnSphere(self.baseOfGun.x, self.baseOfGun.y, self.baseOfGun.z,
                                    self.lenghtOfGun, self.direction, self.angle)
        
        return minecraft.Vec3(x, y, z)
        
    def drawGunInMC(self, blockType, blockData=None):
        x, y, z = findPointOnSphere(self.baseOfGun.x, self.baseOfGun.y, self.baseOfGun.z,
                                    self.lenghtOfGun-1, self.direction, self.angle)
        self.mcDrawing.drawLine(self.baseOfGun.x, self.baseOfGun.y, self.baseOfGun.z,
                                x, y, z,
                                blockType, blockData)

    def drawGun(self):
        self.drawGunInMC(block.WOOL.id, 15)
    
    def clearGun(self):
        self.drawGunInMC(block.AIR)
    
    def setDirection(self, direction):
        #Value validation
        if direction < 0 or direction > 360:
            raise ValueError("direction must be an angle 0 - 360 degrees")
        self.clearGun()
        self.direction = direction
        self.endOfGun = self.findEndOfGun()
        self.drawGun()

    def setAngle(self, angle):
        #Value validation
        if angle < 0 or angle > 90:
            raise ValueError("angle must be between 0 - 90 degrees")
        self.clearGun()
        self.angle = angle
        self.endOfGun = self.findEndOfGun()
        self.drawGun()

# Class to manage the command line interface
class CannonCommands(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "Stuffaboutcode.com Cannon >> "
        self.intro  = "Minecraft Cannon - www.stuffaboutcode.com"

    def do_exit(self, args):
        "Exit cannon [exit]"
        self.cannon.clearCannon()
        return -1

    def do_start(self, args):
        "Start cannon and create it [start]"
        self.mc = minecraft.Minecraft.create()
        playerPos = self.mc.player.getTilePos()
        self.cannon = MinecraftCannon(self.mc, minecraft.Vec3(playerPos.x + 3, playerPos.y, playerPos.z))

    def do_fire(self, args):
        "Fire the cannon [fire]"
        bullet = self.cannon.fire(1, 3)
        while(bullet.update()):
            time.sleep(0.01)

    def do_rotate(self, direction):
        "Rotate cannon [rotate <angle>]"
        self.cannon.setDirection(int(direction))

    def do_tilt(self, angle):
        "Tilt cannon [tilt <angle>]"
        self.cannon.setAngle(int(angle))

    def do_EOF(self, line):
        return True

#main program
if __name__ == "__main__":
    CannonCommands().cmdloop()
