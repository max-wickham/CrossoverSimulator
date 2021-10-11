import numpy as np 
import matplotlib.pyplot as plt
import math

class Component:
    def __init__(self,val, power, node0, node1):
        self.val = val
        self.power = power
        self.node0 = node0
        self.node1 = node1
    def impedance(self,omega):
        return (self.val * pow(omega,self.power))

class Circuit:

    def __init__(self, components, nodes, output_node0, output_node1):
        self.nodes = nodes
        self.components = components
        self.output_node0 = output_node0
        self.output_node1 = output_node1

    def solve(self, omega, impedance):
        self.components.append(Component(impedance,0,self.output_node0,self.output_node1))
        matrix = []
        currents = []
        for i in range(self.nodes):
            matrix.append([])
            currents.append(0)
            for j in range(self.nodes):
                matrix[i].append(0)
        for component in self.components:
            if component.node0 != 0:
                matrix[component.node0-1][component.node0-1] += component.impedance(omega)
                if component.node1 != 0:
                    matrix[component.node0-1][component.node1-1] -= component.impedance(omega)
            if component.node1 != 0:
                matrix[component.node1-1][component.node1-1] += component.impedance(omega)
                if component.node0 != 0:
                    matrix[component.node1-1][component.node0-1] -= component.impedance(omega)
        matrix[0][self.nodes-1] = 1
        matrix[self.nodes-1][0] = 1
        currents[self.nodes-1] = 1
        result = list(np.matmul(np.linalg.inv(matrix),currents))
        if self.output_node1 == 0:
            return -1 * result[self.output_node0-1]
        if self.output_node0 == 0:
            return result[self.output_node1-1]
        self.components.pop()
        #print(result)
        return result[self.output_node1-1] - result[self.output_node0-1]


r1 = Component(100,0,2,3)
c1 = Component(1/(complex(0,0.01)),-1,1,2)
r2 = Component(0.001,0,3,0)

circuit = Circuit([r1,c1,r2],3, 2, 3)

print(abs(circuit.solve(10000,1)))

freq = []
val = []
for i in range(1,10000):
    freq.append(i)
    val.append(abs(circuit.solve(i,1)))

plt.plot(freq,val)
plt.show