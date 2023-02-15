import random
import math
import time

from common import run, neighborhood


def simulated_annealing(S0, T0, temp_decay, n_iter):
	print("Simulated Annealing")
	print(f"S0={S0}, T0={T0}, temp_decay={temp_decay}, n_iter={n_iter}")

	S_best = S0
	E_best = cost(S0)
	S = S0
	E = E_best
	neighbors = neighborhood(S0)
	T = T0
	
	S_list = [S_best]
	E_list = [E_best]

	for k in range(n_iter):
		S_new = random.choice(neighbors)
		E_new = cost(S_new)
		print(f"[{k}/{n_iter}] {S_new} {E_new}", end='')
		if E_new > E or random.random() < math.exp(-(E-E_new)/T):
			S = S_new
			E = E_new
			neighborhs = neighborhood(S)
			if E > E_best:
				S_best = S
				E_best = E
			print(" ACCEPTED")
		else:
			print(" REJECTED")
		T = temp_decay(T)
		
		S_list.append(S)
		E_list.append(E)
	
	return S_best, E_best, S_list, E_list

def cost(S0):
	total = 0
	for i in range(3):
		total += run(S0)
	return total/3


def decay_geometric(T):
	return 0.9*T


if __name__ == "__main__":
	S0 = ["Ofast", "avx512", 32, 16, 16, 16]
	T0 = 100
	n_iter = 20

	t0 = time.time()
	S_best, E_best, S_list, E_list = simulated_annealing(S0, T0, decay_geometric, n_iter)
	t = time.time() - t0

	print()
	print("Best solution:", S_best, "with", E_best, "Gflops")
	print("Time:", t)
	print("===")
	print(E_list)
	print(S_list)

