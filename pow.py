'''
A sample code to show how to proof the work, and show how long it need. x is
last block's proof, y is new block's proof that we need to find out.

'''
from hashlib import sha256
from time import time

x = 5
y = 0  # y is unknow number

start = time()
while sha256(f'{x}{y}'.encode()).hexdigest()[:4] != "0000":
    y += 1
    print(f'The solution is y ={y}')
end = time()

print(end - start)
