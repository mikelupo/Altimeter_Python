from numpy import angle

# # Anton's code which I've amply hacked up ##

# clock.py  By Anton Vredegoor (anton.vredegoor@gmail.com) 
# last edit: july 2009,
# license: GPL
# enjoy!


"""
A very simple  clock.


The program transforms worldcoordinates into screencoordinates 
and vice versa according to an algorithm found in: "Programming 
principles in computer graphics" by Leendert Ammeraal.


"""


from Tkinter import *
from time import localtime
from datetime import timedelta,datetime
from math import sin, cos, pi
import sys, types, os
from PIL import ImageTk, Image


_inidle = type(sys.stdin) == types.InstanceType and \
      sys.stdin.__class__.__name__ == 'PyShell'


class transformer:


    def __init__(self, world, viewport):
        self.world = world 
        self.viewport = viewport


    def point(self, x, y):
        x_min, y_min, x_max, y_max = self.world
        X_min, Y_min, X_max, Y_max = self.viewport
        f_x = float(X_max-X_min) /float(x_max-x_min) 
        f_y = float(Y_max-Y_min) / float(y_max-y_min) 
        f = min(f_x,f_y)
        x_c = 0.5 * (x_min + x_max)
        y_c = 0.5  * (y_min + y_max)
        X_c = 0.5  * (X_min + X_max)
        Y_c = 0.5  * (Y_min + Y_max)
        c_1 = X_c - f * x_c
        c_2 = Y_c - f * y_c
        X = f * x + c_1
        Y = f * y + c_2
        return X , Y


    def twopoints(self,x1,y1,x2,y2):
        return self.point(x1,y1),self.point(x2,y2)


class clock:


    def __init__(self,root,deltahours = 0):
        self.world       = [-1,-1,1,1]
        self.bgcolor     = '#000000'
        self.bgimage     = os.path.join(os.path.dirname(__file__), "Altimeter.jpg")
        self.circlecolor = '#808080'
        self.timecolor   = '#ffffff'
        self.ten_th_color = '#FFFF00'
        self.circlesize  = 0.09
        self._ALL        = 'all'
        self.pad         = 25
        self.root        = root
        WIDTH, HEIGHT = 400, 400
        self.thousands_needle_radius = 0.570    #length of the thousands needle.
        self.testaltitude = 0.00
        
        # Altimeter clock constants
        self.Kphi_tens_tickmark = 0.72  #the angle between each tens of feet tick mark. (needed for thousands feet needle placement)


        #hitting the escape key kills the altimeter app.
        root.bind("<Escape>", lambda _ : root.destroy())
        self.delta = timedelta(hours = deltahours)  


        self.canvas = Canvas(root, 
                width       = WIDTH,
                height      = HEIGHT,
                background  = self.bgcolor)


        self.original_image = Image.open(self.bgimage)
        size = WIDTH, HEIGHT
        resized = self.original_image.resize(size,Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(resized)       

        viewport = (self.pad,self.pad,WIDTH-self.pad,HEIGHT-self.pad)
        self.T = transformer(self.world,viewport)
        self.root.title('Clock')

        self.canvas.bind("<Configure>",self.resize)
        self.canvas.pack(fill=BOTH, expand=YES)
        self.poll()
 
    def resize(self, event):
        size = (event.width, event.height)
        resized = self.original_image.resize(size,Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(resized)
        #self.canvas.delete("IMG")
        self.canvas.create_image(0, 0, image=self.image, anchor=NW, tags="IMG")
        self.redraw()
    
    def configure(self):
        self.redraw()
    
    def redraw(self):
        sc = self.canvas
        sc.delete(self._ALL)
        width = sc.winfo_width()
        height =sc.winfo_height()
        #~ sc.create_rectangle([[0,0],[width,height]],
                #~ fill = self.bgcolor, tag = self._ALL)
        self.canvas.create_image(0, 0, image=self.image, anchor=NW, tags="IMG")
        viewport = (self.pad,self.pad,width-self.pad,height-self.pad)
        self.T = transformer(self.world,viewport)
        self.paintgrafics()


    def paintgrafics(self):
        start = -pi/2
        step = pi/5
        for i in range(0,10):
            angle =  start+i*step
            x, y = cos(angle),sin(angle)
            #self.paintnumber(x,y,i)
            #self.paintcircle(x, y)
        self.painthms()
        #self.paintcircle(0,0)
    
    #paints the hands of the clock.
    def painthms(self):
        T = datetime.timetuple(datetime.utcnow()-self.delta)
        self.testaltitude = self.testaltitude + 20
        current_altitude = self.testaltitude
        ten_thousands_of_feet = current_altitude / 10000
        thousands_of_feet = current_altitude / 1000
        hundreds_of_feet = current_altitude / 100

        x,x,x,h,m,s,x,x,x = T
        self.root.title('%02i:%02i:%02i' %(h,m,s))
        ft_thousands = 4 #(o'clock position)
        ft_tens = 20 #two hundred
        #a line object that we'll reuse a few times below.
        scl= self.canvas.create_line

        #https://en.wikipedia.org/wiki/Clock_angle_problem

        m=hundreds_of_feet
        h=thousands_of_feet
        s=ten_thousands_of_feet
        
        #angle and placement of the second hand
        angle = -pi/2 + (pi/25)*s
        x, y = cos(angle)*.95,sin(angle)*.95   
        scl(apply(self.T.twopoints, [0,0,x,y]), fill = self.ten_th_color,
                    tag =self._ALL, arrow = 'last')

        #Hour hand
        #angle = -pi/2 + (pi/5)*h + (pi/5)*(m/50.0)
        angle = -pi/2 + (pi/5)*(m/50.0)
        print angle
        print h
        r=self.thousands_needle_radius
        x, y = cos(angle)*r, sin(angle)*r
        scl(apply(self.T.twopoints,[0,0,x,y]), fill = self.timecolor, 
                    tag =self._ALL, width = 6, arrow='last')        

        #angle and placement of MINUTE hand.
        angle = -pi/2 + (pi/25)*m #+ (pi/25)*(s/50.0)
        x, y = cos(angle)*.80,sin(angle)*.80
        scl(apply(self.T.twopoints,[0,0,x,y]), fill = self.timecolor, 
                    tag =self._ALL, width = 8, arrow = 'last')
       


    def paintcircle(self,x,y):
        ss = self.circlesize / 2.0
        mybbox = [-ss+x,-ss+y,ss+x,ss+y]
        sco = self.canvas.create_oval
        sco(apply(self.T.twopoints,mybbox), fill = self.circlecolor,
                    tag =self._ALL)


    def poll(self):
        self.configure()
        self.root.after(100,self.poll)


def main():
    root= Tk()
    # deltahours: how far are you from utc?
    # someone should automatize that, but I sometimes want to display
    # time as if I am in another timezone ...
    clock(root,deltahours = -8)
    if not _inidle:
        root.mainloop()


if __name__=='__main__':
  main()