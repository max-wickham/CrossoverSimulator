	

from typing import Dict
import gi
import cairo
import math
from dataclasses import dataclass

import schemdraw
import schemdraw.elements as elm

from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas)
from matplotlib.figure import Figure
import numpy as np

import matplotlib
#matplotlib.use('inline')
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

@dataclass
class Speaker:
    name : str
    responseChooser : Gtk.Widget
    impedanceChooser : Gtk.Widget

@dataclass
class Component:
    name : str
    valueChooser : Gtk.Widget

class Resistor(Component):
    def print(self):
        return

class Capacitor(Component):
    def print(self):
        return

class Inductor(Component):
    def print(self):
        return

class GridSquare(Gtk.EventBox):
    def __init__(self,xPos,yPos):
        super().__init__()
        self.set_size_request(15,15)
        self.pos = (xPos,yPos)
        self.selected = False

class MainWindow(Gtk.Window):

    # component grid state

    speakers : Dict[str,Speaker] = {}
    components : Dict[str,Component] = {}
    speakerCounter = 0
    resistorCounter = 0
    inductorCounter = 0
    capacitorCounter = 0

    #design box state

    xRange = 50
    yRange = 30
    squares = [[] for i in range(xRange)]
    waiting = False
    lastCoordinate = (0,0)

    def __init__(self):
        super().__init__(title="Crossover Designer")
        self.__constructMainGrid()
        self.__constructComponentButtons()
        #self.__constructDesignGrid()
        self.__constructPreview()
        self.add(self.mainGrid)

    # main grid

    def __constructMainGrid(self):
        self.mainGrid = Gtk.Grid()
        self.leftGrid = Gtk.Grid()
        self.rightGrid = Gtk.Grid()

        self.buttonGrid = Gtk.Grid()
        self.mainGrid.attach(self.buttonGrid,0,0,1,1)

        self.speakerGrid = Gtk.Grid()
        self.mainGrid.attach(self.speakerGrid,0,1,1,1)
        self.designBox = Gtk.Grid(column_homogeneous=True, row_homogeneous=True)
        self.mainGrid.attach(self.designBox,1,0,1,1)
        self.graphBox = Gtk.Box()
        self.mainGrid.attach(self.graphBox,1,1,1,1)

    # design grid

    def __constructPreview(self):
        import matplotlib 
        print(matplotlib.get_backend())
        d = schemdraw.Drawing()
        d.add(elm.Resistor())
        d.add(elm.Capacitor())
        d.add(elm.Diode())
        figure = d.draw(show = False)
        import matplotlib.pyplot as plt  # type: ignore
        canvas = FigureCanvas(figure.fig)  # a Gtk.DrawingArea
        canvas.set_size_request(600, 600)
        self.designBox.add(canvas)
        self.show_all()

    def __constructDesignGrid(self):
        if self.squares[0] == []:
            for i in range(self.xRange):
                for j in range(self.yRange):
                    eventBox = GridSquare(i,j)
                    eventBox.connect("event", self.__hoverButton)
                    eventBox.connect("button-press-event", self.__gridClicked)
                    self.designGrid.attach(eventBox, i, j, 1, 1)
                    self.squares[i].append(eventBox)
            self.designGrid.set_row_spacing(0)
        for i in range(self.xRange):
            for j in range(self.yRange):
                box = self.squares[i][j]
                if self.waiting:
                    box = self.squares[self.lastCoordinate[0]][self.lastCoordinate[1]]
                    if box.get_child(): box.remove(box.get_child())
                    box.add(Gtk.Image.new_from_file('icons/orange.png'))
                elif box.selected:
                    if box.get_child(): box.remove(box.get_child())
                    box.add(Gtk.Image.new_from_file('icons/white.png'))
                else: 
                    if box.get_child(): box.remove(box.get_child())
                    box.add(Gtk.Image.new_from_file('icons/grey.png'))
        self.show_all()

    def __hoverButton(self, widget : GridSquare, third):
        return

    def __gridClicked(self, widget : GridSquare, x):
        print("lastCoordinate",self.lastCoordinate,"pos",widget.pos)
        if self.waiting == False:
            self.waiting = True
            self.lastCoordinate = widget.pos
            self.__constructDesignGrid()
            return
        widget.clicked = False
        self.waiting = False

        minimum = min(self.lastCoordinate[1],widget.pos[1])
        maximum = max(self.lastCoordinate[1],widget.pos[1])
        for i in range(min(minimum, maximum),max(minimum, maximum)+1):
            box = self.squares[self.lastCoordinate[0]][i]
            box.selected = True
        minimum = min(self.lastCoordinate[0],widget.pos[0])
        maximum = max(self.lastCoordinate[0],widget.pos[0])
        for i in range(min(minimum, maximum),max(minimum, maximum)+1):
            box = self.squares[i][widget.pos[1]]
            box.selected = True
        self.__constructDesignGrid()

    # component buttons

    def __constructComponentButtons(self):
        self.resistorButton = Gtk.Button(label="Resistor")
        self.resistorButton.connect("clicked", self.__resistorClicked)
        self.buttonGrid.attach(self.resistorButton,0,0,2,1)

        self.capacitorButton = Gtk.Button(label="Capacitor")
        self.capacitorButton.connect("clicked", self.__capacitorClicked)
        self.buttonGrid.attach(self.capacitorButton,0,1,2,1)

        self.inductorButton = Gtk.Button(label="Inductor")
        self.inductorButton.connect("clicked", self.__inductorClicked)
        self.buttonGrid.attach(self.inductorButton,0,2,2,1)

        self.speakerButton = Gtk.Button(label="Speaker")
        self.speakerButton.connect("clicked", self.__speakerClicked)
        self.buttonGrid.attach(self.speakerButton,0,3,2,1)

    def __addComponent(self, klass, name):
        component = klass(name, Gtk.Entry())
        self.components[name] = component
        self.__constructComponentGrid()

    def __resistorClicked(self, widget):
        name = "Resistor" + str(self.resistorCounter)
        self.resistorCounter += 1
        self.__addComponent(Resistor, name)

    def __capacitorClicked(self, widget):
        name = "Capacitor" + str(self.capacitorCounter)
        self.capacitorCounter += 1
        self.__addComponent(Capacitor, name)

    def __inductorClicked(self, widget):
        name = "Inductor" + str(self.inductorCounter)
        self.inductorCounter += 1
        self.__addComponent(Inductor, name)

    def __speakerClicked(self, widget):
        name = "Speaker" + str(self.speakerCounter)
        speaker = Speaker(name, Gtk.Entry(), Gtk.Entry())
        self.speakerCounter += 1
        self.speakers[name] = speaker
        self.__constructComponentGrid()

    # component grid
    
    def __constructComponentGrid(self):
        for widget in self.speakerGrid.get_children():
            self.speakerGrid.remove(widget)
        count = 0 
        for speaker in self.speakers.values():
            nameLabel = Gtk.Label(label=speaker.name)
            responseChooseLabel = Gtk.Label(label="FRD File")
            impedanceChooseLabel = Gtk.Label(label="ZMA File")
            self.speakerGrid.attach(nameLabel,0,count,2,1)
            self.speakerGrid.attach(speaker.responseChooser,1,count+1,1,1)
            self.speakerGrid.attach(speaker.impedanceChooser,1,count+2,1,1)
            self.speakerGrid.attach(impedanceChooseLabel,0,count+1,1,1)
            self.speakerGrid.attach(responseChooseLabel,0,count+2,1,1)
            count += 3
        for component in self.components.values():
            nameLabel = Gtk.Label(label=component.name)
            valueLabel = Gtk.Label(label="Value")
            self.speakerGrid.attach(nameLabel,0,count,2,1)
            self.speakerGrid.attach(component.valueChooser,1,count+1,1,1)
            self.speakerGrid.attach(valueLabel,0,count+1,1,1)
            count += 2
        self.show_all()
                                
win = MainWindow()
win.set_default_size(640, 480)
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
