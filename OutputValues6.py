# Output page for our text file
# Command should be
#           >> py OutputValues4.py demofile.txt



# ******Text file format********
# 1 [temp] [volume] [volume]
# 2 [number_of_coordinates]
# 3 [x] [y]
# 4 [etc]



# imports

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.logger import Logger
from kivy.uix.image import Image

import sys
import numpy as np
import matplotlib.pyplot as plt



def values():
    global tem
    global vol
    global mas
    global den
    #print(path+" dfsfs")
    f = open("sensor.txt", "r")
    #print(f.readline())
    vals = f.readline().split(" ")
    tem = round(float(vals[0]),3)
    vol = round(float(vals[1])*12.3*8.5,3)
    mas = round(float(vals[2]),3)
    den = round(mas/vol,3)

    
    #adding coordinates
    x = []
    y = []
    for i in range(int(f.readline())):
        s = f.readline()
        coord = s.split(" ")
        x.append(int(coord[0]))
        y.append(int(coord[1]))
        
    # Plot
    colors = (0,0,0)
    area = np.pi*3
    
    plt.scatter(x, y, s=area, c=colors, alpha=0.5)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.savefig('lightPlt')


# Boxlayout is the App class
class outputPage(BoxLayout):
    global img
    def __init__(self,**kwargs):
        super(outputPage,self).__init__(**kwargs)
        #values(10.2,23.3,23.2)
        self.title = 'Values'
        self.orientation='vertical' #possible for error

        photoBox        = BoxLayout(orientation='horizontal')
        photos          = BoxLayout(orientation='horizontal')
        photoTitle       = Label(text = "Light Spectra:")
        photoPlot       = Image(source = "lightPlt.png")
        photoSoil       = Image(source = "SoilColour.jpg")
        
        photoBox.add_widget(photoTitle)
        photos.add_widget(photoPlot)
        photos.add_widget(photoSoil)
        photoBox.add_widget(photos)
        

        verticalBox     = BoxLayout(orientation='vertical')
        #temperature
        temperature     = BoxLayout(orientation='horizontal')
        tempTitle       = Label(text = "Temperature:\n(C)", halign = 'center')
        tempValue       = Label(text = ""+str(tem))
        temperature.add_widget(tempTitle)
        temperature.add_widget(tempValue)
        
        #volume
        volume          = BoxLayout(orientation='horizontal')
        volTitle        = Label(text = "Volume\n(cm^3)", halign = 'center')
        volValue        = Label(text = ""+str(vol))
        volume.add_widget(volTitle)
        volume.add_widget(volValue)
        
        #mass
        mass            = BoxLayout(orientation='horizontal')
        massTitle       = Label(text = "Mass:\n(g)", halign = 'center')
        massValue       = Label(text = str(mas))
        mass.add_widget(massTitle)
        mass.add_widget(massValue)
        
        #density
        density         = BoxLayout(orientation='horizontal')
        densTitle       = Label(text = "Density:\n(g/cm^3)", halign = 'center')
        densValue       = Label(text = str(den))
        density.add_widget(densTitle)
        density.add_widget(densValue)

 

        verticalBox.add_widget(temperature)
        verticalBox.add_widget(volume)
        verticalBox.add_widget(mass)
        #verticalBox.add_widget(density)

        horizontalBox   = BoxLayout(orientation='vertical')
        button1         = Button(text="Menu")
        button1.bind(on_press=self.agafunc)
        button3         = Button(text="Close")
        button3.bind(on_press=self.clsfunc)
        horizontalBox.add_widget(density)
        #horizontalBox.add_widget(button1)
        horizontalBox.add_widget(button3)
   
        self.add_widget(photoBox)    
        self.add_widget(verticalBox)
        
        self.add_widget(horizontalBox)
    def clsfunc (self,obj):
        App.get_running_app().stop()
        Window.close()

    def agafunc (self,obj):
        Window.close()
   
class Application(App):
    def on_stop(self):
        Logger.critical('Goodbye')
    def build(self):
        self.title= "Zoroak 777 Values"
        return outputPage()

# Instantiate and run the kivy app

if __name__ == '__main__':
    values();
    Application().run()
