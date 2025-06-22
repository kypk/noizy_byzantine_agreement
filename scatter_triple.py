import matplotlib.pyplot as plt
import math
import sys

data1 = []
data2 = []
data3 = []
with open(sys.argv[1]) as file:
    for row in file:
        data1.append(row.split(','))
with open(sys.argv[2]) as file:
    for row in file:
        data2.append(row.split(','))
with open(sys.argv[3]) as file:
    for row in file:
        data3.append(row.split(','))


m = [int(d[0]) for d in data1]
p1 = [float(d[1]) for d in data1]
p2 = [float(d[1]) for d in data2]
p3 = [float(d[1]) for d in data3]
error1=[]
error2=[]
error3=[]
p_e = []

mu = 0.272
l = 0.94
def multinomial(lst):
    res, i = 1, sum(lst)
    i0 = lst.index(max(lst))
    for a in lst[:i0] + lst[i0+1:]:
        for j in range(1,a+1):
            res *= i
            res //= j
            i -= 1
    return res

faulty = sys.argv[4]
if faulty == "No": 
    for m_value in m:
        T = math.ceil(mu*m_value)
        Q = T - math.ceil(T*l) + 1
        exact_probability = 0.0
        for i in range(T):
            exact_probability += math.comb(m_value, i)*((1/3)**i)*((2/3)**(m_value-i))
        p_e.append(exact_probability)
elif faulty == "S":
    for m_value in m:
        T = math.ceil(mu*m_value)
        Q = T - math.ceil(T*l) + 1
        _sum = 0.0
        for l3 in range(T, m_value-T+1):
            for l1 in range(T-Q, m_value-Q-l3+1):
                _sum += multinomial([l3, l1, m_value-l1-l3]) 
        lower = _sum*((1/3)**m_value)*(2**(-Q))
        exact_probability = lower + 1 - _sum*((1/3)**m_value)
        p_e.append(exact_probability)
elif faulty == "R0":
    for m_value in m:
        T = math.ceil(mu*m_value)
        Q = T - math.ceil(T*l) + 1
        lower = 0.0
        for l1 in range(T, m_value-T+1):
            for l2 in range(T-Q+1):
                l3 = m_value - l1 - l2
                _sum = 0.0
                for k in range(T-Q+1-l2, T-l2+1):
                    _sum += math.comb(T-l2, k)*((2/3)**k)*((1/3)**(T-l2-k))
                lower += multinomial([l1, l2, l3])*((1/3)**l1)*((1/6)**l2)*((1/2)**l3)*_sum
        for l1 in range(T, m_value-T+1):
            for l2 in range(T-Q+1, m_value-l1+1):
                lower += multinomial([l1, l2, l3])*((1/3)**l1)*((1/6)**l2)*((1/2)**l3)
        for l1 in range(T):
            lower += math.comb(m_value, l1)*((1/3)**l1)*((2/3)**(m_value-l1))
        exact_probability = lower
        for l1 in range(m_value-T+1, m_value+1):
            exact_probability += math.comb(m_value, l1)*((1/3)**l1)*((2/3)**(m_value-l1))
        p_e.append(exact_probability)

for p_i in p1:
    error1.append(math.sqrt(p_i*(1-p_i)/1000))
for p_i in p2:
    error2.append(math.sqrt(p_i*(1-p_i)/1000))
for p_i in p3:
    error3.append(math.sqrt(p_i*(1-p_i)/1000))

# Create scatter plot
plt.scatter(m, p_e, facecolors='none', edgecolors='g', linewidths=2, marker='o', label="Upper Bounds")
#plt.errorbar(m, p, fmt='rx', yerr=0.01, markeredgewidth=2, capsize=3.0)
plt.errorbar(m, p1, fmt='rx', yerr=error1, markeredgewidth=2, capsize=0.0)
plt.errorbar(m, p2, fmt='bx', yerr=error2, markeredgewidth=2, capsize=0.0)
plt.errorbar(m, p3, fmt='yx', yerr=error3, markeredgewidth=2, capsize=0.0)
plt.scatter(m, p1, facecolors='r', linewidths=2, marker='x', label="Near-Term")
plt.scatter(m, p2, facecolors='b', linewidths=2, marker='x', label="3x Improved")
plt.scatter(m, p3, facecolors='y', linewidths=2, marker='x', label="10x Improved")
#plt.legend(loc="right", fontsize=20)

# Add labels and title
plt.xlabel('Number of four-qubit singlet states, m', fontsize=20)
plt.ylabel('Failure Probability', fontsize=20)
plt.title(f"{faulty} Faulty", fontsize=20)

plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
plt.ylim(-0.02, 1.02)
plt.subplots_adjust(top=0.5)

#plt.savefig(sys.argv[1].split('.')[0] + ".png")

# Show plot
plt.show()
