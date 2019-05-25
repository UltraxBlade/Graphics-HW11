import mdl
from display import *
from matrix import *
from Graphics import *
import math

class WorldStack:
    def __init__(self):
        self.L=[I(4)]
    def push(self):
        self.L.append([r[:] for r in self.L[len(self.L)-1]])
    def peek(self):
        return self.L[len(self.L)-1]
    def pop(self):
        return self.L.pop(len(self.L)-1)

def run(filename):
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print("Parsing failed.")
        return
    
    img=generate(501,501)
    zbuff=zbuffer(501,501,501)
    world=WorldStack()
    if "_default" not in symbols:
        symbols['_default'] = ['constants',
                             {'red': [0.2, 0.5, 0.5],
                              'green': [0.2, 0.5, 0.5],
                              'blue': [0.2, 0.5, 0.5]}]
    edgeColor=[0,0,0]
    #print(symbols)
    frames=None
    baseName=None
    vary=[]
    for command in commands:
        if command["op"]=="frames":
            frames=int(command["args"][0])
        if command["op"]=="basename":
            baseName=command["args"][0]
        if command["op"]=="vary":
            vary.append(command)
    if baseName==None:
        print("No base name given. Setting base name to 'image'.")
        baseName="image"
    if frames==None:
        if len(vary)>0:
            print("Error: 'vary' found, but no frame count given")
        else:
            for command in commands:
                #print(command)
                edges=[[],[],[],[]]
                polys=[[],[],[],[]]
                transform=world.peek()
                coords=command["args"][:]
                if command["op"]=="set_default":
                    if command["constants"]!=None:
                        symbols["_default"]=symbols[command["constants"]]
                    else:
                        symbols["_default"]=['constants',
                                             {'red': [coords[0], coords[1], coords[2]],
                                              'green': [coords[3], coords[4], coords[5]],
                                              'blue': [coords[6], coords[7], coords[8]]}]
                polyColor=symbols["_default"][1]
                if command["op"]=="push":
                    world.push()
                elif command["op"]=="pop":
                    world.pop()
                elif command["op"]=="move":
                    transform=multMatrix(transform,translate(coords[0],coords[1],coords[2]))
                    for r in range(len(world.peek())):
                        world.peek()[r]=transform[r]
                elif command["op"]=="scale":
                    transform=multMatrix(transform,scale(coords[0],coords[1],coords[2]))
                    for r in range(len(world.peek())):
                        world.peek()[r]=transform[r]
                elif command["op"]=="rotate":
                    transform=multMatrix(transform,rotate(coords[0],float(coords[1])))
                    for r in range(len(world.peek())):
                        world.peek()[r]=transform[r]
                elif command["op"]=="box":
                    box(polys,coords[0],coords[1],coords[2],coords[3],coords[4],coords[5])
                    if command["constants"]!=None:
                        polyColor=symbols[command["constants"]][1]
                elif command["op"]=="sphere":
                    sphere(polys,coords[0],coords[1],coords[2],coords[3])
                    if command["constants"]!=None:
                        polyColor=symbols[command["constants"]][1]
                elif command["op"]=="torus":
                    torus(polys,coords[0],coords[1],coords[2],coords[3],coords[4])
                    if command["constants"]!=None:
                        polyColor=symbols[command["constants"]][1]
                elif command["op"]=="triangle":
                    addPoly(polys,coords[0],coords[1],coords[2],coords[3],coords[4],coords[5],coords[6],coords[7],coords[8])
                    if command["constants"]!=None:
                        polyColor=symbols[command["constants"]][1]
                elif command["op"]=="line":
                    addEdge(edges,coords[0],coords[1],coords[2],coords[3],coords[4],coords[5])
                elif command["op"]=="save":
                    save_extension(img,command["args"][0]+".png")
                elif command["op"]=="display":
                    display(img)
                if len(edges[0])>0:
                    edges=multMatrix(transform,edges)
                    drawLines(img,zbuff,edges,edgeColor)
                if len(polys[0])>0:
                    polys=multMatrix(transform,polys)
                    drawPolys(img,zbuff,polys,polyColor)
    else:
        knobs={}
        for command in vary:
            #print(command)
            if command["knob"] in knobs:
                vals=knobs[command["knob"]]
            else:
                vals=[None]*frames
            dval=command["args"][3]-command["args"][2]
            nframes=command["args"][1]-command["args"][0]
            for i in range(int(command["args"][0]),int(command["args"][1]+1)):
                vals[i]=command["args"][2]+dval*((i-command["args"][0])/nframes)
            knobs[command["knob"]]=vals
        for knob in knobs.keys():
            lastFound=None
            firstFound=None
            vals=knobs[knob]
            for i in range(len(vals)):
                if vals[i]==None:
                    vals[i]=lastFound
                else:
                    if firstFound==None:
                        firstFound=vals[i]
                    lastFound=vals[i]
            for i in range(len(vals)):
                if vals[i]==None:
                    vals[i]=firstFound
            knobs[knob]=vals
        #print(knobs)
        for frame in range(frames):
            img=generate(501,501)
            zbuff=zbuffer(501,501,501)
            world=WorldStack()
            for command in commands:
                #print(command)
                edges=[[],[],[],[]]
                polys=[[],[],[],[]]
                transform=world.peek()
                coords=None
                if command["args"]!=None:
                    coords=command["args"][:]
                #print(coords)
                if command["op"]=="set_default":
                    if command["constants"]!=None:
                        symbols["_default"]=symbols[command["constants"]]
                    else:
                        symbols["_default"]=['constants',
                                             {'red': [coords[0], coords[1], coords[2]],
                                              'green': [coords[3], coords[4], coords[5]],
                                              'blue': [coords[6], coords[7], coords[8]]}]
                polyColor=symbols["_default"][1]
                if command["op"]=="push":
                    world.push()
                elif command["op"]=="pop":
                    world.pop()
                elif command["op"]=="move":
                    if "knob" in command.keys() and command["knob"]!=None:
                        for i in range(len(coords)):
                            coords[i]=coords[i]*knobs[command["knob"]][frame]
                    #print(coords)
                    transform=multMatrix(transform,translate(coords[0],coords[1],coords[2]))
                    for r in range(len(world.peek())):
                        world.peek()[r]=transform[r]
                elif command["op"]=="scale":
                    if "knob" in command.keys() and command["knob"]!=None:
                        for i in range(len(coords)):
                            coords[i]=coords[i]*knobs[command["knob"]][frame]
                    #print(coords)
                    transform=multMatrix(transform,scale(coords[0],coords[1],coords[2]))
                    for r in range(len(world.peek())):
                        world.peek()[r]=transform[r]
                elif command["op"]=="rotate":
                    if "knob" in command.keys() and command["knob"]!=None:
                        coords[1]=coords[1]*knobs[command["knob"]][frame]
                    #print(coords)
                    transform=multMatrix(transform,rotate(coords[0],float(coords[1])))
                    for r in range(len(world.peek())):
                        world.peek()[r]=transform[r]
                elif command["op"]=="box":
                    box(polys,coords[0],coords[1],coords[2],coords[3],coords[4],coords[5])
                    if command["constants"]!=None:
                        polyColor=symbols[command["constants"]][1]
                elif command["op"]=="sphere":
                    sphere(polys,coords[0],coords[1],coords[2],coords[3])
                    if command["constants"]!=None:
                        polyColor=symbols[command["constants"]][1]
                elif command["op"]=="torus":
                    torus(polys,coords[0],coords[1],coords[2],coords[3],coords[4])
                    if command["constants"]!=None:
                        polyColor=symbols[command["constants"]][1]
                elif command["op"]=="triangle":
                    addPoly(polys,coords[0],coords[1],coords[2],coords[3],coords[4],coords[5],coords[6],coords[7],coords[8])
                    if command["constants"]!=None:
                        polyColor=symbols[command["constants"]][1]
                elif command["op"]=="line":
                    addEdge(edges,coords[0],coords[1],coords[2],coords[3],coords[4],coords[5])
                elif command["op"]=="save":
                    save_extension(img,command["args"][0]+".png")
                elif command["op"]=="display":
                    display(img)
                if len(edges[0])>0:
                    edges=multMatrix(transform,edges)
                    drawLines(img,zbuff,edges,edgeColor)
                if len(polys[0])>0:
                    polys=multMatrix(transform,polys)
                    drawPolys(img,zbuff,polys,polyColor)
                if frame==0:
                    numZeroes=int(math.log10(frames))
                else:
                    numZeroes=int(math.log10(frames))-int(math.log10(frame))
            #print(frame)
            save_extension(img,"anim/"+baseName+("0"*numZeroes)+str(frame)+".png")
        make_animation(baseName)
