import numpy as np
x = [[1,2],[2,3]]
currents = [1,0]
inverse = np.linalg.inv(x)
result = np.matmul(inverse,currents)
print(list(result))
