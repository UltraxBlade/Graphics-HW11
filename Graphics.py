#! /usr/bin/python3
import math
from matrix import *

bgcolor=[255,255,255]
view=normalize([0,0,1])
ambient=[50,50,50]
light=[normalize([0.5,0.75,1]),[255,255,255]]
spower=4

def generate(width,height,color=bgcolor):
    global bgcolor
    bgcolor=color
    return [[bgcolor[:] for i in range(width)] for j in range(height)]

def zbuffer(width,height,color):
    return [[float("-inf") for i in range(width)] for j in range(height)]

def output(fileName, img):
    out="P3\n"+str(len(img[0]))+" "+str(len(img))+"\n255\n"
    for row in img:
        for pixel in row:
            for color in pixel:
                out+=str(color)+" "
            out+=" "
        out+="\n"
    f=open(fileName,"w")
    f.write(out)
    f.close()

def clear(img,zbuffer):
    for i in range(len(img)):
        for j in range(len(img[i])):
            img[i][j]=bgcolor[:]
            zbuffer[i][j]=float("-inf")

def fadeRing(img,minRad,maxRad,centerX,centerY,color):
    centerRow=len(img)-centerY
    centerCol=centerX
    for rad in range(minRad,maxRad):
        for row in range(len(img)):
            if(rad**2-(row-centerRow)**2)>=0:
                if(int(round(math.sqrt(rad**2-(row-centerRow)**2)+centerCol))<len(img[row]))and(int(round(math.sqrt(rad**2-(row-centerRow)**2)+centerCol))>=0):
                    img[row][int(round(math.sqrt(rad**2-(row-centerRow)**2)+centerCol))]=color[:]
                if(int(round(-math.sqrt(rad**2-(row-centerRow)**2)+centerCol))<len(img[row]))and(int(round(-math.sqrt(rad**2-(row-centerRow)**2)+centerCol))>=0):
                    img[row][int(round(-math.sqrt(rad**2-(row-centerRow)**2)+centerCol))]=color[:]
    return img

def ring(img,minRad,maxRad,centerX,centerY,color):
    centerRow=len(img)-centerY
    centerCol=centerX
    for row in range(len(img)):
        for col in range(len(img[row])):
            if (row-centerRow)**2+(col-centerCol)**2>=minRad**2 and (row-centerRow)**2+(col-centerCol)**2<=maxRad**2:
                img[row][col]=color[:]
    return img
    
def rect(img,width,height,TLX,TLY,color):
    TLrow=len(img)-TLY
    TLcol=TLX
    for row in range(height):
        for col in range(width):
            if TLrow+row<len(img) and TLcol+col<len(img[0]):
                img[TLrow+row][TLcol+col]=color[:]
    return img

def line(img,zbuffer,x0,y0,z0,x1,y1,z1,color):
    r0=len(img)-y0
    r1=len(img)-y1
    c0=x0
    c1=x1
    z=z0
    if r0>r1:
        start=[r1,c1,z1]
        end=[r0,c0,z0]
    elif r0<r1:
        start=[r0,c0,z0]
        end=[r1,c1,z1]
    elif c0>c1:
        start=[r1,c1,z1]
        end=[r0,c0,z0]
    else:
        start=[r0,c0,z0]
        end=[r1,c1,z1]
    drow=end[0]-start[0]
    dcol=end[1]-start[1]
    z0=start[2]
    z1=end[2]
    if drow==0:
        if dcol!=0:
            dz=(z1-z0)/(dcol)
            col=start[1]
            row=start[0]
            while col<end[1]:
                if row>=0 and row<len(img) and col>=0 and col<len(img[row]):
                    if int(z*1000)/1000.0>=zbuffer[row][col]:
                        zbuffer[row][col]=z
                        img[row][col]=color[:]
                col+=1
                z+=dz
        else:
            z=max(z0,z1)
            if r0>=0 and c0>=0 and r0<len(zbuffer) and c0<len(zbuffer[r0]) and int(z*1000)/1000.0>zbuffer[r0][c0]:
                zbuffer[r0][c0]=z
                img[r0][c0]=color[:]
    else:
        slope=dcol/drow
        if slope>=0 and slope<=1:
            dz=(z1-z0)/(drow)
            row=start[0]
            col=start[1]
            d=2*dcol-drow
            drow*=2
            dcol*=2
            while(row<=end[0]):
                if row>=0 and row<len(img) and col>=0 and col<len(img[row]): 
                    if int(z*1000)/1000.0>=zbuffer[row][col]:
                        zbuffer[row][col]=z
                        img[row][col]=color[:]
                #c=((c1-c0)/(r1-r0))(r-r0)+c0
                if d>0:
                    col+=1
                    d-=drow
                row+=1
                d+=dcol
                z+=dz
        elif slope>1:
            dz=(z1-z0)/(dcol)
            row=start[0]
            col=start[1]
            d=dcol-2*drow
            drow*=2
            dcol*=2
            while(col<=end[1]):
                if row>=0 and row<len(img) and col>=0 and col<len(img[row]):
                    if int(z*1000)/1000.0>=zbuffer[row][col]:
                        zbuffer[row][col]=z
                        img[row][col]=color[:]
                #c=((c1-c0)/(r1-r0))(r-r0)+c0
                if d<0:
                    row+=1
                    d+=dcol
                col+=1
                d-=drow
                z+=dz
        elif slope<0 and slope>=-1:
            dz=(z1-z0)/(drow)
            row=start[0]
            col=start[1]
            d=2*dcol+drow
            drow*=2
            dcol*=2
            while(row<=end[0]):
                if row>=0 and row<len(img) and col>=0 and col<len(img[row]):
                    if int(z*1000)/1000.0>=zbuffer[row][col]:
                        zbuffer[row][col]=z
                        img[row][col]=color[:]
                #c=((c1-c0)/(r1-r0))(r-r0)+c0
                if d<0:
                    col-=1
                    d+=drow
                row+=1
                d+=dcol
                z+=dz
        elif slope<-1:
            dz=(z1-z0)/(dcol)
            row=start[0]
            col=start[1]
            d=dcol+2*drow
            drow*=2
            dcol*=2
            while(col>=end[1]):
                if row>=0 and row<len(img) and col>=0 and col<len(img[row]):
                    if int(z*1000)/1000.0>=zbuffer[row][col]:
                        zbuffer[row][col]=z
                        img[row][col]=color[:]
                #c=((c1-c0)/(r1-r0))(r-r0)+c0
                if d>0:
                    row+=1
                    d+=dcol
                col-=1
                d+=drow
                z+=dz
    return img

def addPoint(edges,x,y,z):
    edges[0].append(x)
    edges[1].append(y)
    edges[2].append(z)
    edges[3].append(1)
def addEdge(edges,x0,y0,z0,x1,y1,z1):
    addPoint(edges,x0,y0,z0)
    addPoint(edges,x1,y1,z1)
def drawLines(img,zbuffer,edges,color):
    for col in range(0,len(edges[0])-1,2):
        line(img,zbuffer,int(edges[0][col]),int(edges[1][col]),int(edges[2][col]),int(edges[0][col+1]),int(edges[1][col+1]),int(edges[2][col+1]),color[:])

def translate(dx,dy,dz):
    M=I(4)
    M[0][3]=dx
    M[1][3]=dy
    M[2][3]=dz
    return M

def scale(dx,dy,dz):
    M=I(4)
    M[0][0]=dx
    M[1][1]=dy
    M[2][2]=dz
    return M

def rotate(axis,theta):
    theta=math.radians(theta)
    M=I(4)
    if axis=="x":
        M[1][1]=math.cos(theta)
        M[1][2]=-math.sin(theta)
        M[2][1]=math.sin(theta)
        M[2][2]=math.cos(theta)
    elif axis=="y":
        M[2][2]=math.cos(theta)
        M[2][0]=-math.sin(theta)
        M[0][2]=math.sin(theta)
        M[0][0]=math.cos(theta)
    elif axis=="z":
        M[0][0]=math.cos(theta)
        M[0][1]=-math.sin(theta)
        M[1][0]=math.sin(theta)
        M[1][1]=math.cos(theta)
    return M

def circle(edges,cx,cy,cz,r,steps=100):
    prevX=cx+r
    prevY=cy
    step=1
    while step<=steps:
        t=step/steps
        x=cx+r*math.cos(t*2*math.pi)
        y=cy+r*math.sin(t*2*math.pi)
        addEdge(edges,prevX,prevY,cz,x,y,cz)
        prevX=x
        prevY=y
        step+=1

def hermite(edges,x0,y0,x1,y1,rx0,ry0,rx1,ry1,steps=100):
    given=[[x0,y0],[x1,y1],[rx0,ry0],[rx1,ry1]]
    M=[[2,-2,1,1],[-3,3,-2,-1],[0,0,1,0],[1,0,0,0]]
    coeffs=multMatrix(M,given)
    step=1
    prevX=x0
    prevY=y0
    while step<=steps:
        t=step/steps
        tMat=[[t*t*t,t*t,t,1]]
        point=multMatrix(tMat,coeffs)
        addEdge(edges,prevX,prevY,0,point[0][0],point[0][1],0)
        prevX=point[0][0]
        prevY=point[0][1]
        step+=1

def bezier(edges,x0,y0,x1,y1,x2,y2,x3,y3,steps=100):
    given=[[x0,y0],[x1,y1],[x2,y2],[x3,y3]]
    M=[[-1,3,-3,1],[3,-6,3,0],[-3,3,0,0],[1,0,0,0]]
    coeffs=multMatrix(M,given)
    step=1
    prevX=x0
    prevY=y0
    while step<=steps:
        t=step/steps
        tMat=[[t*t*t,t*t,t,1]]
        point=multMatrix(tMat,coeffs)
        addEdge(edges,prevX,prevY,0,point[0][0],point[0][1],0)
        prevX=point[0][0]
        prevY=point[0][1]
        step+=1

def addPoly(polys,x1,y1,z1,x2,y2,z2,x3,y3,z3):
    addPoint(polys,x1,y1,z1)
    addPoint(polys,x2,y2,z2)
    addPoint(polys,x3,y3,z3)

def drawPolys(img,zbuffer,edges,color):
    global view,ambient,light
    areflect=[color["red"][0],color["green"][0],color["blue"][0]]
    dreflect=[color["red"][1],color["green"][1],color["blue"][1]]
    sreflect=[color["red"][2],color["green"][2],color["blue"][2]]
    for col in range(0,len(edges[0])-1,3):
        v1=[edges[0][col+1]-edges[0][col],edges[1][col+1]-edges[1][col],edges[2][col+1]-edges[2][col]]
        v2=[edges[0][col+2]-edges[0][col],edges[1][col+2]-edges[1][col],edges[2][col+2]-edges[2][col]]
        norm=normalize(crossProduct(v1,v2))
        if dotProduct(norm,view)>0:
            Ia=[areflect[0]*ambient[0],areflect[1]*ambient[1],areflect[2]*ambient[2]]
            Id=[light[1][0]*dreflect[0]*(dotProduct(light[0],norm)),
                light[1][1]*dreflect[1]*(dotProduct(light[0],norm)),
                light[1][2]*dreflect[2]*(dotProduct(light[0],norm))]
            sCalc=dotProduct(subtractVector(scaleVector(2*dotProduct(light[0],norm),norm),light[0]),view)
            if sCalc<0:
                sCalc=0
            Is=[light[1][0]*sreflect[0]*(sCalc**spower),
                light[1][1]*sreflect[1]*(sCalc**spower),
                light[1][2]*sreflect[2]*(sCalc**spower)]
            for i in range(len(Id)):
                if Id[i]<0:
                    Id[i]=0
            for i in range(len(Is)):
                if Is[i]<0:
                    Is[i]=0
            color=[Ia[0]+Id[0]+Is[0],Ia[1]+Id[1]+Is[1],Ia[2]+Id[2]+Is[2]]
            for i in range(len(color)):
                if color[i]>255:
                    color[i]=255
                if color[i]<0:
                    color[i]=0
                color[i]=int(color[i])
            scanLineConvert(img,zbuffer,edges[0][col],edges[1][col],edges[2][col],edges[0][col+1],edges[1][col+1],edges[2][col+1],edges[0][col+2],edges[1][col+2],edges[2][col+2],color)
            """if colorChoice%3==0:
                scanLineConvert(img,zbuffer,edges[0][col],edges[1][col],edges[2][col],edges[0][col+1],edges[1][col+1],edges[2][col+1],edges[0][col+2],edges[1][col+2],edges[2][col+2],[255,0,0])
            if colorChoice%3==1:
                scanLineConvert(img,zbuffer,edges[0][col],edges[1][col],edges[2][col],edges[0][col+1],edges[1][col+1],edges[2][col+1],edges[0][col+2],edges[1][col+2],edges[2][col+2],[0,255,0])
            if colorChoice%3==2:
                scanLineConvert(img,zbuffer,edges[0][col],edges[1][col],edges[2][col],edges[0][col+1],edges[1][col+1],edges[2][col+1],edges[0][col+2],edges[1][col+2],edges[2][col+2],[0,0,255])
            colorChoice+=1"""
            #line(img,zbuffer,int(edges[0][col]),int(edges[1][col]),int(edges[2][col]),int(edges[0][col+1]),int(edges[1][col+1]),int(edges[2][col+1]),color[:])
            #line(img,zbuffer,int(edges[0][col+1]),int(edges[1][col+1]),int(edges[2][col+1]),int(edges[0][col+2]),int(edges[1][col+2]),int(edges[2][col+2]),color[:])
            #line(img,zbuffer,int(edges[0][col]),int(edges[1][col]),int(edges[2][col]),int(edges[0][col+2]),int(edges[1][col+2]),int(edges[2][col+2]),color[:])

def scanLineConvert(img,zbuffer,x0,y0,z0,x1,y1,z1,x2,y2,z2,color):
    y0=int(y0)
    y1=int(y1)
    y2=int(y2)
    if y0==min(y0,y1,y2):
        B=[x0,y0,z0]
        if y1==max(y0,y1,y2):
            T=[x1,y1,z1]
            M=[x2,y2,z2]
        else:
            M=[x1,y1,z1]
            T=[x2,y2,z2]
    elif y1==min(y0,y1,y2):
        B=[x1,y1,z1]
        if y0==max(y0,y1,y2):
            T=[x0,y0,z0]
            M=[x2,y2,z2]
        else:
            M=[x0,y0,z0]
            T=[x2,y2,z2]
    else:
        B=[x2,y2,z2]
        if y0==max(y0,y1,y2):
            T=[x0,y0,z0]
            M=[x1,y1,z1]
        else:
            M=[x0,y0,z0]
            T=[x1,y1,z1]
    if T[1]==B[1]:
        return
    x0=B[0]
    x1=B[0]
    y=B[1]
    z0=B[2]
    z1=B[2]
    dx0=(T[0]-B[0])/(T[1]-B[1])
    dz0=(T[2]-B[2])/(T[1]-B[1])
    if M[1]!=B[1]:
        dx1=(M[0]-B[0])/(M[1]-B[1])
        dz1=(M[2]-B[2])/(M[1]-B[1])
        while y<=M[1]:
            line(img,zbuffer,int(x0),int(y),int(z0),int(x1),int(y),int(z1),color[:])
            y+=1
            x0+=dx0
            x1+=dx1
            z0+=dz0
            z1+=dz1
        x0-=dx0
        z0-=dz0
    x1=M[0]
    z1=M[2]
    y=M[1]
    if T[1]!=M[1]:
        dx1=(T[0]-M[0])/(T[1]-M[1])
        dz1=(T[2]-M[2])/(T[1]-M[1])
        while y<=T[1]:
            line(img,zbuffer,int(x0),int(y),int(z0),int(x1),int(y),int(z1),color[:])
            y+=1
            x0+=dx0
            x1+=dx1
            z0+=dz0
            z1+=dz1

def box(polys,x,y,z,width,height,depth):
    addPoly(polys,x,y,z,x+width,y-height,z,x+width,y,z)
    addPoly(polys,x,y,z,x,y-height,z,x+width,y-height,z)
    addPoly(polys,x,y,z,x,y,z-depth,x,y-height,z-depth)
    addPoly(polys,x,y,z,x,y-height,z-depth,x,y-height,z)
    addPoly(polys,x,y,z,x+width,y,z,x,y,z-depth)
    addPoly(polys,x,y,z-depth,x+width,y,z,x+width,y,z-depth)
    addPoly(polys,x,y-height,z,x,y-height,z-depth,x+width,y-height,z)
    addPoly(polys,x,y-height,z-depth,x+width,y-height,z-depth,x+width,y-height,z)
    addPoly(polys,x,y,z-depth,x+width,y,z-depth,x+width,y-height,z-depth)
    addPoly(polys,x,y,z-depth,x+width,y-height,z-depth,x,y-height,z-depth)
    addPoly(polys,x+width,y,z,x+width,y-height,z-depth,x+width,y,z-depth)
    addPoly(polys,x+width,y,z,x+width,y-height,z,x+width,y-height,z-depth)
    
def sphere(polys,cx,cy,cz,r,steps=100):
    points=spherePoints(cx,cy,cz,r,steps)
    for col in range(len(points[0])):
        addPoly(polys,points[0][col],points[1][col],points[2][col],points[0][(col+steps+1)%len(points[0])],points[1][(col+steps+1)%len(points[0])],points[2][(col+steps+1)%len(points[0])],points[0][(col+1)%len(points[0])],points[1][(col+1)%len(points[0])],points[2][(col+1)%len(points[0])])
        addPoly(polys,points[0][(col+1)%len(points[0])],points[1][(col+1)%len(points[0])],points[2][(col+1)%len(points[0])],points[0][(col+steps+1)%len(points[0])],points[1][(col+steps+1)%len(points[0])],points[2][(col+steps+1)%len(points[0])],points[0][(col+steps+2)%len(points[0])],points[1][(col+steps+2)%len(points[0])],points[2][(col+steps+2)%len(points[0])])
        
def spherePoints(cx,cy,cz,r,steps):
    points=[[],[],[],[]]
    step=0
    while step<steps:
        step2=0
        while step2<=steps:
            t=step2/steps
            x=r*math.cos(t*math.pi)
            y=r*math.sin(t*math.pi)
            addPoint(points,x,y,0)
            step2+=1
        points=multMatrix(rotate("x",360/steps),points)
        step+=1
    points=multMatrix(translate(cx,cy,cz),points)
    return points

def torus(polys,cx,cy,cz,r,R,steps=100):
    points=torusPoints(cx,cy,cz,r,R,steps)
    for col in range(len(points[0])):
        addPoly(polys,points[0][col],points[1][col],points[2][col],points[0][(col+1)%len(points[0])],points[1][(col+1)%len(points[0])],points[2][(col+1)%len(points[0])],points[0][(col+steps+1)%len(points[0])],points[1][(col+steps+1)%len(points[0])],points[2][(col+steps+1)%len(points[0])])
        addPoly(polys,points[0][(col+1)%len(points[0])],points[1][(col+1)%len(points[0])],points[2][(col+1)%len(points[0])],points[0][(col+steps+2)%len(points[0])],points[1][(col+steps+2)%len(points[0])],points[2][(col+steps+2)%len(points[0])],points[0][(col+steps+1)%len(points[0])],points[1][(col+steps+1)%len(points[0])],points[2][(col+steps+1)%len(points[0])])
        
def torusPoints(cx,cy,cz,r,R,steps):
    points=[[],[],[],[]]
    step=0
    while step<steps:
        step2=0
        while step2<=steps:
            t=step2/steps
            x=R+r*math.cos(t*2*math.pi)
            y=r*math.sin(t*2*math.pi)
            addPoint(points,x,y,0)
            step2+=1
        points=multMatrix(rotate("y",360/steps),points)
        step+=1
    points=multMatrix(translate(cx,cy,cz),points)
    return points
