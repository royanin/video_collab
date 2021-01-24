import time
import uuid
import string
import random

N = 100000
t1 = time.time()
for i in range(0,N):
    u = uuid.uuid4()
    v = u.hex
t2 = time.time()
print(t2 - t1)

t3 = time.time()
for i in range(0, N):
    ''.join(random.choice(string.ascii_letters + string.digits) for x in range(10))
t4 = time.time()

print(t4 - t3)
