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
        self.components.append(Component(impedance,0,output_node0,output_node1))
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
        #print(omega)
        #print(matrix)
        #print(currents)
        result = np.matmul(np.linalg.inv(matrix),currents)
        result = list(result)
        if self.output_node1 == 0:
            return -1 * result[self.output_node0-1]
        if self.output_node0 == 0:
            return result[self.output_node1-1]
        self.components.pop()
        return result[self.output_node1-1] - result[self.output_node0-1]



def solve(omega,components,nodes,output_node0,output_node1):
    matrix = []
    currents = []
    for i in range(nodes):
        matrix.append([])
        currents.append(0)
        for j in range(nodes):
            matrix[i].append(0)
    for component in components:
        if component.node0 != 0:
            matrix[component.node0-1][component.node0-1] += component.impedance(omega)
            if component.node1 != 0:
                matrix[component.node0-1][component.node1-1] -= component.impedance(omega)
        if component.node1 != 0:
            matrix[component.node1-1][component.node1-1] += component.impedance(omega)
            if component.node0 != 0:
                matrix[component.node1-1][component.node0-1] -= component.impedance(omega)
    matrix[0][nodes-1] = 1
    matrix[nodes-1][0] = 1
    currents[nodes-1] = 1
    result = np.matmul(np.linalg.inv(matrix),currents)
    result = list(result)
    if node1 == 0:
        return -1 * result[node0-1]
    if node0 == 0:
        return result[node1-1]
    return result[node1-1] - result[node0-1]


data = "impedance.zma"
impedance_list = [[],[]]
with open ("impedance.zma","r") as myfile:
    data = myfile.readlines()    
    for line in data:
        line = line.split("\t")
        impedance_list[0].append(float(line[0]))
        impedance_list[1].append(float(line[1]))
print("input netlist file name")
filename = "netlist2.txt"

data = ""
with open (filename,"r") as myfile:
    data = myfile.readlines()
_file = data
powers = {"m":0.001,"u":0.000001,"n":1}
circuit = []
output_node1 = 0
output_node0 = 0
nodes = 0
components = []
impedance = 8
for line in _file:
    val = complex(0,0)
    power = 0
    words = line.split(" ")
    if words[0] == 'I1':
        output_node1 = int(words[1])
        continue
    if words[0] == 'I0':
        output_nodes0 = int(words[1])
        continue
    if words[0] == 'S':
        impedance = float(words[1])
        continue
    value = words[1]
    suffix = value[len(value)-1]
    value = float(value[:len(value)-1])
    prefix_power = powers[suffix]
    
    if words[0] == 'C':
        val =complex(0, -1 / (value * prefix_power))
        power = -1
    if words[0] == 'L':
        val = complex(0,value * prefix_power)
        power = 1
    if words[0] == 'R':
        val =complex( value * prefix_power,0)
        power = 0
    print(words)   
    node0 = int(words[2])
    node1 = int(words[3])
    if node0 > nodes:
        nodes = node0
    if node1 > nodes:
        nodes = node1
    component = Component(val,power,node0,node1)
    components.append(component)
circuit = Circuit(components, nodes, output_node0, output_node1)
for component in components:
    print(component.impedance(100))

input_freq = []
input_mag = []
print("input magnitude response filenames")
results = []
magnitude_response_filenames = ("response.frd output.frd").split(" ")
for magnitude_response_filename in magnitude_response_filenames:
    input_freq = []
    input_mag = []
    magnitude_response = []
    with open(magnitude_response_filename,"r") as myfile:
        _magnitude_response = myfile.readlines()
        for _response in _magnitude_response:
            response = ""
            response = _response[0]
            for i in range(1,len(_response)):
                if _response[i] == " " and _response[i-1] == " ":
                    continue
                response += _response[i]
            magnitude_response.append(response)
       # print(magnitude_response)
    freq = []
    response = []
    for line in magnitude_response:
        #print(line)
        line = line[:-1]
        line = line.split("\t")
        #print(line)
        frequency = float(line[0])
        magnitude = float(line[1])
        input_freq.append(frequency)
        input_mag.append(magnitude)
        #print(frequency)
        #print(magnitude)
        #response.append( float(magnitude) *abs( solve(frequency / (2*3.14), components, nodes, output_node0, output_node1)))
        impedance = 0
        for i in range(len(impedance_list[0])):
            if frequency > impedance_list[0][i]:
                impedance = impedance_list[1][i]
                break
        #response.append( float(magnitude)  + 2 * math.log( abs( circuit.solve(frequency / (2*3.14), impedance)) ,10) )
        response.append(2 * math.log(abs(circuit.solve(frequency * (2*3.14), impedance)),10))
        freq.append(frequency)
    #print(response)
    results.append([freq,response])

num = 0
if len(results) > 1:
    for result in results[0:1]:
        for pair in results[1]:
            frequency = pair[0]
            for i in range(num,len(result[0])-1):
                if result[0][i] < frequency and result[0][i] > frequency:
                    magnitude = result[1][i] + (result[1][i+1] - result[1][i]) * (result[0][i+1] - result[0][i]) / (result[0][i+1] - pair[0])
                    result[0][i] = pair[0]
                    result[1][i] = magnitude
                    num = i
min_len = len(results[0])
#for result in results[1:]:
#    if len(result) < min_len:
#        min_len = len(result)

#for i in range(len(results)):
#    results[i] = results[i][:min_len]
#print(results[1])
#frequencies = []
#magnitudes = []
#for i in range(len(results[1][0])):
#    total = 0
#    frequencies.append(results[1][0][i])
#    for result in results:
        #print(result)
#        total += result[1][i]
#    total /= len(results)
#    magnitudes.append(total)

#print(results[0][1])
#print(input_freq)
print(len(input_freq))
print(len(results[1][1]))
plt.plot(results[0][0],results[0][1])
#plt.show()
#plt.plot(input_freq,input_mag)
plt.show()
