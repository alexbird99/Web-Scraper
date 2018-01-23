import numpy as np
import matplotlib.pyplot as plt

def interest(rate, year):
    final = pow(1 + rate, year)
    return final

print(interest(0.08, 33))

# evenly sampled time at 1 year intervals
# t = np.arange(0., 31., 1)
# fig, ax = plt.subplots()

# ax.plot(t, interest(0.01, t), 'b', label='1%')
# ax.plot(t, interest(0.05, t), 'g', label='5%')
# ax.plot(t, interest(0.10, t), 'k', label='10%')
# ax.plot(t, interest(0.20, t), 'r', label='20%')
# #ax.plot(t, interest(0.15, t), 'ko')

t = np.arange(0., 11., 1)
fig, ax = plt.subplots()
ax.plot(t, interest(0.10, t), 'b', label='10%')
ax.plot(t, interest(0.15, t), 'g', label='15%')
ax.plot(t, interest(0.20, t), 'k', label='20%')
ax.plot(t, interest(0.25, t), 'r', label='25%')
ax.plot(t, interest(0.30, t), 'y', label='30%')

legend = ax.legend(loc='upper center', shadow=True, fontsize='x-large')
plt.ylabel("times")    
plt.xlabel("years")
plt.show()