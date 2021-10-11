import schemdraw
import schemdraw.elements as elm

d = schemdraw.Drawing()
d.add(elm.Resistor())
d.add(elm.Capacitor())
d.add(elm.Diode())
d.show = False
figure = d.draw()
figure.show()