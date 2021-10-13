from typing import Dict, List, Tuple
from dataclasses import dataclass
import numpy as np 
import matplotlib.pyplot as plt
import math
from abc import ABC, abstractmethod

@dataclass
class Component:

    node0 : int
    node1 : int

    @abstractmethod
    def impedance(self, omega : float) -> complex:
        pass

@dataclass
class StandardComponent(Component):

    val : float

@dataclass
class Resistor(StandardComponent):

    def impedance(self, omega : float) -> complex:
        return self.val

@dataclass
class Capacitor(StandardComponent):

    def impedance(self, omega : float) -> complex:
        return pow(omega * complex(0,self.val),-1)

@dataclass
class Inductor(StandardComponent):

    def impedance(self, omega : float) -> complex:
        return pow(omega * complex(0,self.val))

@dataclass
class Speaker(Component):

    responses : List[Tuple[float,float]]
    impedances : List[Tuple[float,float]]
    maxFrequencyImpedance : int
    maxFrequencyResponse : int
    minFrequencyImpedance : int
    minFrequencyResponse : int

    def impedance(self, omega : float) -> float:
        frequency = omega / (2 * math.pi)
        for impedance in reversed(self.impedances):
            if frequency > impedance[0]: return impedance[1]
        return 0

    def response(self, frequency : float) -> float:
        for response in reversed(self.responses):
            if frequency > response[0]: return response[1]
        return 0

class Circuit:

    def __init__(self,components : List[Component]):
        self.components : List[Component] = []
        self.nodes : int = 0
        self.components = components
        self.nodes = max([max(x.node0,x.node1) for x in self.components]) + 1

    def solve(self, omega : float) -> List[complex]:
        matrix = self.__constructMatrix(omega)
        currents = [0 for i in range(self.nodes -1)]
        # assume 1V at node 1 and 0V at node 0
        currents[0] = 1
        result = np.matmul(np.linalg.inv(matrix),currents)
        result = list(result)
        result.insert(0,0)
        return result

    def __constructMatrix(self, omega : float) -> List[List[complex]]:
        matrix = [ [0 for i in range(self.nodes - 1)] for i in range(self.nodes - 1)]
        matrix[0][0] = 1
        for component in self.components:
            if component.node0 > 1:
                matrix[component.node0-1][component.node0-1] += 1 / component.impedance(omega)
                if component.node1 != 0:
                    matrix[component.node0-1][component.node1-1] -= 1 / component.impedance(omega)
            if component.node1 > 1:
                matrix[component.node1-1][component.node1-1] += 1 / component.impedance(omega)
                if component.node0 != 0:
                    matrix[component.node1-1][component.node0-1] -= 1 / component.impedance(omega)
        return matrix

class CrossOver:

    def __init__(self, netlist : str):
        self.speakers : List[Speaker] = []
        self.circuit = self.__parseNetlist(netlist)


    def __parseNetlist(self, netlist : str) -> Circuit:
        netlist = netlist.split("\n")
        netlist = [line.split(' ') for line in netlist]
        components : List[Component] = []
        for line in netlist:
            if line[0] == "R":
                components.append(Resistor(int(line[1]),int(line[2]),float(line[3])))
                continue
            elif line[0] == "C":
                components.append(Capacitor(int(line[1]),int(line[2]),float(line[3])))
                continue
            elif line[0] == "C":
                components.append(Inductor(int(line[1]),int(line[2]),float(line[3])))
                continue
            elif line[0] == "S":
                responses, minFrequencyResponse, maxFrequencyResponse = self.__generateResponseData(line[3])
                impedances, minFrequencyImpedance, maxFrequencyImpedance = self.__generateImpedanceData(line[4])
                # TODO need to read values
                outputNode0 = int(line[1])
                outputNode1 = int(line[2])
                speaker = Speaker(outputNode0,outputNode1,responses,impedances,
                    maxFrequencyImpedance,maxFrequencyResponse,
                    minFrequencyImpedance, minFrequencyResponse)
                self.speakers.append(speaker)
                components.append(speaker)
        return Circuit(components)

    def __generateResponseData(self, responseFileName : str) -> Tuple[List[float], float, float]:
        file = open(responseFileName,"r")
        responseData = file.read().split('\n')
        responseData = [line.split('\t') for line in responseData]
        file.close()
        maxF = float(responseData[len(responseData)-1][0])
        minF = float(responseData[0][0])
        responses = []
        for line in responseData:
            responses.append((float(line[0]),float(line[1])))
        return responses, minF, maxF

    def __generateImpedanceData(self, responseFileName : str) -> Tuple[List[float], float, float]:
        file = open(responseFileName,"r")
        responseData = file.read().split('\n')
        responseData = [line.split('    \t') for line in responseData]
        file.close()
        maxF = float(responseData[len(responseData)-1][0])
        minF = float(responseData[0][0])
        responses = []
        for line in responseData:
            responses.append((float(line[0]),float(line[1])))
        return responses, minF, maxF

    def generateResponse(self, startF, endF) -> Tuple[List[float],List[float]]:
        frequency : List[float] = [f for f in range(startF,endF)]
        response : List[float] = []
        for f in frequency:
            results = self.circuit.solve(f * 2 * math.pi)
            totalMag : complex = 0
            for speaker in self.speakers:
                mag = results[speaker.node1] - results[speaker.node0]
                mag *= speaker.response(f) / 100
                totalMag += mag
            response.append(abs(totalMag))
        return (frequency, response)


file = open("netlist.txt", "r")
netlist = file.read()
file.close()
crossOver = CrossOver(netlist)
frequency, response = crossOver.generateResponse(500,10000)
plt.plot(frequency,response)
plt.show()