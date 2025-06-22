from application import SenderProgram, Receiver0Program, Receiver1Program

from squidasm.run.stack.config import StackNetworkConfig # type: ignore
from squidasm.run.stack.run import run # type: ignore
from netsquid.util.simtools import set_random_state

import multiprocessing as mp
import argparse

# import network configuration from file
cfg = StackNetworkConfig.from_file("config_nv.yaml")

# Create instances of programs to run
receiver1_program = Receiver1Program()

# Run the simulation. Programs argument is a mapping of network node labels to programs to run on that node
def run_simulation(min_m, max_m, mu, l, faulty, n):
    results = []
    for m in range(min_m, max_m+1, 10):
        result = run(config=cfg, programs={"Sender": SenderProgram(m=m, mu=mu, l=l, faulty=faulty), "Receiver0": Receiver0Program(faulty=faulty), "Receiver1": receiver1_program}, num_times=n)
        fails = 0
        for i in range(n):
            values = [result[0][i]["ys"], result[1][i]["y0"], result[2][i]["y1"]] # [ys, y0, y1]
            if (faulty == "s"):
                if (values[0] is None):
                    fails += 1
                elif (values[1:] == [0, 1] or values[1:] == [1, 0]):
                    fails += 1
            elif (faulty == "r0"):
                if (values[1] is None):
                    fails += 1
                elif (values[2] != 0):
                    fails += 1
            elif (values != [0, 0, 0] and values != [1, 1, 1]):
                fails += 1
        results.append((m, fails))
    return results

def run_simulation_parallel(arg_list):
    # Set a unique seed for each run
    set_random_state(arg_list[0])
    
    # Your SquidASM experiment setup here
    result = run_simulation(*arg_list[1:])
    
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--faulty", default="")
    parser.add_argument("-m", default="20,400")
    parser.add_argument("--mu", default=0.272)
    parser.add_argument("-l", default=0.94)
    args=parser.parse_args()

    N = 100

    faulty = args.faulty
    min_m = int(args.m.split(',')[0])
    max_m = int(args.m.split(',')[1])
    mu = float(args.mu)
    l = float(args.l)

    num_cores = mp.cpu_count()  # Detect available cores
    seeds = range(num_cores)    # Example: one simulation per core
    args = [[seed, min_m, max_m, mu, l, faulty, int(N/num_cores)] for seed in seeds]
    args[-1][-1] += N % num_cores
    
    with mp.Pool(processes=num_cores) as pool:
        results = pool.map(run_simulation_parallel, args)

    # Aggregate and analyze results
    probabilities = []
    for m in range(min_m, max_m+1, 10):
        sum = 0
        for r in results:
            for row in r:
                if (row[0] == m):
                    sum += row[1]
        prob = sum/N
        probabilities.append((m, prob))

    for p in probabilities:
        print(f"{p[0]},{p[1]}")