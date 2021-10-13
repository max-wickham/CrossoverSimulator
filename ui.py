	

from typing import Dict, List
import gi
from dataclasses import dataclass
from abc import ABC, abstractmethod

import schemdraw
import schemdraw.elements as elm

from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas)
from matplotlib.figure import Figure
import numpy as np

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

@dataclass
class Component:
    name : str
    node0Chooser : Gtk.Entry
    node1Chooser : Gtk.Entry

    @abstractmethod
    def createComponent(self):
        pass

@dataclass
class Speaker(Component):
    responseChooser : Gtk.Entry 
    impedanceChooser : Gtk.Entry

    def createComponent(self):
        return elm.Diode()

@dataclass
class StandardComponent(Component):
    valueChooser : Gtk.Widget

class Resistor(StandardComponent):
    def print(self):
        return
    
    def createComponent(self):
        return elm.Resistor()

class Capacitor(StandardComponent):
    def print(self):
        return

    def createComponent(self):
        return elm.Capacitor()

class Inductor(StandardComponent):
    def print(self):
        return
    
    def createComponent(self):
        return elm.Inductor()

class MainWindow(Gtk.Window):

    def __init__(self):
        super().__init__(title="Crossover Designer")

        # component grid state

        self.components : Dict[str,Component] = {}
        self.speakerCounter = 0
        self.resistorCounter = 0
        self.inductorCounter = 0
        self.capacitorCounter = 0

        # preview state

        self.calculatorState = ""
        self.drawing = schemdraw.Drawing()

        # construct layout

        self.__constructMainGrid()
        self.__constructComponentButtons()
        self.__constructPreview()
        self.add(self.mainGrid)

    # main grid

    def __constructMainGrid(self):
        self.mainGrid = Gtk.Grid()
        
        self.leftGrid = Gtk.Grid()
        self.rightGrid = Gtk.Grid()
        self.mainGrid.attach(self.leftGrid,0,0,1,1)
        self.mainGrid.attach(self.rightGrid,1,0,1,1)

        self.buttonGrid = Gtk.Grid()
        self.leftGrid.attach(self.buttonGrid,0,0,1,1)
        self.speakerGrid = Gtk.Grid()
        self.leftGrid.attach(self.speakerGrid,0,1,1,1)

        self.designBox = Gtk.Grid(column_homogeneous=True, row_homogeneous=True)
        self.rightGrid.attach(self.designBox,0,0,1,1)
        self.graphBox = Gtk.Box()
        self.rightGrid.attach(self.graphBox,0,1,1,1)

    # design preview

    def __constructPreview(self):
        import matplotlib 
        print(matplotlib.get_backend())
        d = self.drawing
        figure = d.draw(show = False)
        import matplotlib.pyplot as plt  # type: ignore
        canvas = FigureCanvas(figure.fig)  # a Gtk.DrawingArea
        canvas.set_size_request(600, 400)
        self.designBox.add(canvas)
        self.show_all()

    # component buttons

    def __constructComponentButtons(self):
        self.resistorButton = Gtk.Button(label="Resistor")
        self.resistorButton.connect("clicked", self.__resistorClicked)
        self.buttonGrid.attach(self.resistorButton,0,0,1,1)

        self.capacitorButton = Gtk.Button(label="Capacitor")
        self.capacitorButton.connect("clicked", self.__capacitorClicked)
        self.buttonGrid.attach(self.capacitorButton,0,1,1,1)

        self.inductorButton = Gtk.Button(label="Inductor")
        self.inductorButton.connect("clicked", self.__inductorClicked)
        self.buttonGrid.attach(self.inductorButton,0,2,1,1)

        self.speakerButton = Gtk.Button(label="Speaker")
        self.speakerButton.connect("clicked", self.__speakerClicked)
        self.buttonGrid.attach(self.speakerButton,0,3,1,1)

        self.calculateButton = Gtk.Button(label="Calculate")
        self.calculateButton.connect("clicked", self.__calculateClicked)
        self.buttonGrid.attach(self.calculateButton,1,0,1,2)

    def __calculateClicked(self,widget):
        self.drawing = schemdraw.Drawing()
        nodes : Dict[int, object] = {}
        components = list(self.components.values())
        components.sort(key = 
            lambda x : min(int(x.node0Chooser.get_text()),int(x.node1Chooser.get_text())))
        source = self.drawing.add(elm.Source().left())
        nodes[0] = source.start
        nodes[1] = source.end
        count = 0
        for component in components:
            count += 1
            item = component.createComponent()
            print(nodes.keys())
            node0 = int(component.node0Chooser.get_text())
            node1 = int(component.node1Chooser.get_text())
            print("node0",node0,"node1",node1)
            if not node0 in nodes:
                if count == len(components) - 1: 
                    placedItem = self.drawing.add(item.to(nodes[node1]).label(component.name).down())
                else: placedItem = self.drawing.add(item.to(nodes[node1]).label(component.name).left())
                nodes[node0] = placedItem.start
                continue
            if not node1 in nodes:
                if count == len(components) - 1:
                    placedItem = self.drawing.add(item.to(nodes[node0]).label(component.name).down())
                else: placedItem = self.drawing.add(item.to(nodes[node0]).label(component.name).left())
                nodes[node1] = placedItem.start
                continue
            print(component)
            placedItem = self.drawing.add(item.endpoints(nodes[node0],nodes[node1]).label(component.name))
        self.__constructPreview()
        return

    def __addComponent(self, klass, name):
        component = klass(name, Gtk.Entry(), Gtk.Entry(), Gtk.Entry())
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
        speaker = Speaker(name, Gtk.Entry(), Gtk.Entry(), Gtk.Entry(), Gtk.Entry())
        self.speakerCounter += 1
        self.components[name] = speaker
        self.__constructComponentGrid()

    # component grid
    
    def __constructComponentGrid(self):
        # remove old children from tree
        for widget in self.speakerGrid.get_children():
            self.speakerGrid.remove(widget)
        count = 0  
        for component in self.components.values():
            if isinstance(component, Speaker):
                nameLabel = Gtk.Label(label=component.name)
                responseChooseLabel = Gtk.Label(label="FRD File")
                impedanceChooseLabel = Gtk.Label(label="ZMA File")
                node0Label = Gtk.Label(label="Node 0")
                node1Label = Gtk.Label(label="Node 1")
                self.speakerGrid.attach(nameLabel,0,count,2,1)
                self.speakerGrid.attach(component.responseChooser,1,count+1,1,1)
                self.speakerGrid.attach(component.impedanceChooser,1,count+2,1,1)
                self.speakerGrid.attach(impedanceChooseLabel,0,count+1,1,1)
                self.speakerGrid.attach(responseChooseLabel,0,count+2,1,1)
                self.speakerGrid.attach(component.node0Chooser,1,count+3,1,1)
                self.speakerGrid.attach(component.node1Chooser,1,count+4,1,1)
                self.speakerGrid.attach(node0Label,0,count+3,1,1)
                self.speakerGrid.attach(node1Label,0,count+4,1,1)
                count += 5
                continue
            nameLabel = Gtk.Label(label=component.name)
            valueLabel = Gtk.Label(label="Value")
            node0Label = Gtk.Label(label="Node 0")
            node1Label = Gtk.Label(label="Node 1")
            self.speakerGrid.attach(nameLabel,0,count,2,1)
            self.speakerGrid.attach(component.valueChooser,1,count+1,1,1)
            self.speakerGrid.attach(valueLabel,0,count+1,1,1)
            self.speakerGrid.attach(component.node0Chooser,1,count+2,1,1)
            self.speakerGrid.attach(component.node1Chooser,1,count+3,1,1)
            self.speakerGrid.attach(node0Label,0,count+2,1,1)
            self.speakerGrid.attach(node1Label,0,count+3,1,1)
            count += 4
        self.show_all()
                                
win = MainWindow()
win.set_default_size(640, 480)
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
