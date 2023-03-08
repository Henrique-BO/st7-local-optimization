import random
import math
import time

from common import run, neighborhood


def tabu_sa(S0, T0, temp_decay, n_iter, tabu_size):
	print("Tabu Simulated Annealing")
	print(f"S0={S0}, T0={T0}, temp_decay={temp_decay}, n_iter={n_iter}, tabu_size={tabu_size}")

	S_best = S0
	E_best = cost(S0)
	S = S0
	E = E_best
	neighbors = neighborhood(S0)
	T = T0

	Ltabu = [S_best]

	S_list = [S_best]
	E_list = [E_best]

	for k in range(n_iter):
		S_new = random.choice(neighbors)
		while S_new in Ltabu:
			S_new = random.choice(neighbors)
		E_new = cost(S_new)
		print(f"[{k}/{n_iter}] {S_new} {E_new}", end='')
		if E_new > E or random.random() < math.exp(-(E-E_new)/T):
			S = S_new
			E = E_new
			neighbors = neighborhood(S)
			if E > E_best:
				S_best = S
				E_best = E
			Ltabu = fifo_add(S_best, Ltabu, tabu_size)
			print(" ACCEPTED")
		else:
			print(" REJECTED")
		print(Ltabu)
		T = temp_decay(T0, k, n_iter)

		S_list.append(S)
		E_list.append(E)

	return S_best, E_best, S_list, E_list

def cost(S0):
	total = 0
	for i in range(3):
		total += run(S0)
	return total/3

def decay_geometric(T0, k, n_iter):
	a = 10**(math.log10(0.01)/n_iter)
	return (a**k)*T0

def decay_linear(T0, k, n_iter):
	return T0*(1 - k/n_iter)

def fifo_add(S_best, Ltabu, tabu_size):
	if len(Ltabu) == tabu_size:
		Ltabu.pop(0)
	Ltabu.append(S_best)
	return Ltabu



if __name__ == "__main__":
	S0_list = [
		["Ofast", "avx512", 32, 16, 16, 16],
		["Ofast", "avx512", 32, 64, 64, 64],
		["Ofast", "avx512", 32, 32, 32, 32],
#		["Ofast", "avx512", 32, 256, 256, 256],
#		["Ofast", "avx512", 16, 16, 16, 16],
#		['O3', 'avx', 32, 256, 4, 8]
	]
	T0 = 100
	n_iter = 60
	tabu_size = 2

	for S0 in S0_list:
		print("S0:", S0)

		t0 = time.time()
		S_best, E_best, S_list, E_list = tabu_sa(S0, T0, decay_geometric, n_iter, tabu_size)
		t = time.time() - t0

		print()
		print("Best solution:", S_best, "with", E_best, "Gflops")
		print("Time:", t)
		print("===")
		print(E_list)
		print(S_list)
		print()
