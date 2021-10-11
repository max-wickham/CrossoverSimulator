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
    node0 : int
    node1 : int

@dataclass
class Resistor(StandardComponent):

    def impedance(self, omega : float) -> complex:
        return self.val

@dataclass
class Capacitor(StandardComponent):

    def impedance(self, omega : float) -> complex:
        print(omega)
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

    components : List[Component]
    outputNode0 : int
    outputNode1 : int

    def __init__(self, components : List[Component], outputNode0 : int, outputNode1 : int):
        self.nodes = max([max(x.node0,x.node1) for x in components]) + 1
        self.components = components
        self.outputNode0 = outputNode0
        self.outputNode1 = outputNode1

    def solve(self, omega : float) -> complex:
        matrix = [ [0 for i in range(self.nodes - 1)] for i in range(self.nodes - 1)]
        currents = [0 for i in range(self.nodes -1)]
        # contruct matrix
        for component in self.components:
            if component.node0 > 1:
                matrix[component.node0-1][component.node0-1] += 1 / component.impedance(omega)
                if component.node1 != 0:
                    matrix[component.node0-1][component.node1-1] -= 1 / component.impedance(omega)
            if component.node1 > 1:
                matrix[component.node1-1][component.node1-1] += 1 / component.impedance(omega)
                if component.node0 != 0:
                    matrix[component.node1-1][component.node0-1] -= 1 / component.impedance(omega)
        # assume 1V at node 1 and 0V at node 0
        matrix[0][0] = 1
        currents[0] = 1
        result = np.matmul(np.linalg.inv(matrix),currents)
        result = list(result)
        # print(result)
        if self.outputNode1 == 0:
            return -1 * result[self.outputNode0-1]
        if self.outputNode0 == 0:
            return result[self.outputNode1-1]
        return result[self.outputNode1-1] - result[self.outputNode0-1]

class CrossOver:

    circuit : Circuit
    speaker : Speaker

    def __init__(self, netlist : str):
        self.circuit = self._parseNetlist(netlist)


    def _parseNetlist(self, netlist : str) -> Circuit:
        netlist = netlist.split("\n")
        netlist = [line.split(' ') for line in netlist]
        components : List[Component] = []
        outputNode0 : int = 0
        outputNode1 : int = 0
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
                responses, minFrequencyResponse, maxFrequencyResponse = self._generateResponseData(line[3])
                impedances, minFrequencyImpedance, maxFrequencyImpedance = self._generateImpedanceData(line[4])
                # TODO need to read values
                outputNode0 = int(line[1])
                outputNode1 = int(line[2])
                self.speaker = Speaker(outputNode0,outputNode1,responses,impedances,
                    maxFrequencyImpedance,maxFrequencyResponse,
                    minFrequencyImpedance, minFrequencyResponse)
                components.append(self.speaker)
        return Circuit(components,outputNode0,outputNode1)

    def _generateResponseData(self, responseFileName : str) -> Tuple[List[float], float, float]:
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

    def _generateImpedanceData(self, responseFileName : str) -> Tuple[List[float], float, float]:
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
            result = self.circuit.solve(f * 2 * math.pi)
            print(self.speaker.response(f))
            response.append(abs(result) * self.speaker.response(f) / 100)
        return (frequency, response)


file = open("netlist.txt", "r")
netlist = file.read()
file.close()
crossOver = CrossOver(netlist)
frequency, response = crossOver.generateResponse(500,10000)
plt.plot(frequency,response)
plt.show()

# r1 = Component(50,0,1,2)
# r2 = Component(50,0,2,0)
# c1 = Component(pow(complex(0,0.0001),-1),-1,2,0)

# circuit = Circuit([r1,r2,c1],1,2)

#print(abs(circuit.solve(1,1)))

# freq = []
# val = []
# for i in range(1,1000):
#     freq.append(i)
#     val.append(abs(circuit.solve(i,1)))

# plt.plot(freq,val)
# plt.show()