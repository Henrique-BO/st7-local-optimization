import random
import math
import time

from common import run, neighborhood


def tunneling_sa(n1, n2, n3, S0, T0, temp_decay, n_iter, E_tunnel, cost):
	print("Tunneling Simulated Annealing")
	print(f"n1={n1}, n2={n2}, n3={n3}, S0={S0}, T0={T0}, temp_decay={temp_decay}, n_iter={n_iter}, E_tunnel={E_tunnel}")

	S_best = S0
	E_best_tun, E_best = cost(S0, E_tunnel, n1, n2, n3)
	S = S0
	E_tun = E_best_tun
	E = E_best
	neighbors = neighborhood(S0, n1, n2, n3)
	T = T0

	S_list = [S_best]
	E_list = [E_best]

	for k in range(n_iter):
		S_new = random.choice(neighbors)
		E_new_tun, E_new  = cost(S_new, E_tunnel, n1, n2, n3)
		print(f"[{k}/{n_iter}] {S_new} {E_new}", end='')
		if E_new_tun > E_tun or random.random() < math.exp(-(E_tun-E_new_tun)/T):
			S = S_new
			E_tun = E_new_tun
			E = E_new
			neighbors = neighborhood(S, n1, n2, n3)
			if E_tun > E_best_tun:
				S_best = S
				E_best_tun = E_tun
				E_best = E
			print(" ACCEPTED")
		else:
			print(" REJECTED")
		T = temp_decay(T0, k, n_iter)
		
		S_list.append(S)
		E_list.append(E)
	
	return S_best, E_best, S_list, E_list

def cost_average(S0, E_tunnel, n1, n2, n3):
	total = 0
	for i in range(3):
		total += run(S0, n1, n2, n3)
	E = total/3
	if E < E_tunnel:
		return (E + E_tunnel)/2, E
	else:
		return E, E

def cost_stochastic(S0, E_tunnel, n1, n2, n3):
	gamma = 0.004

	total = 0
	for i in range(3):
		total += run(S0, n1, n2, n3)
	E = total/3
	return math.exp(-gamma*(E_tunnel - E)) - 1, E

def decay_geometric(T0, k, n_iter):
	a = 10**(math.log10(0.01)/n_iter)
	return (a**k)*T0

def decay_linear(T0, k, n_iter):
	return T0*(1 - k/n_iter)

if __name__ == "__main__":
	n1 = 256
	n2 = 256
	n3 = 256

	S0_list = [
		["Ofast", "avx512", 32, 16, 16, 16],
#		["Ofast", "avx512", 32, 64, 64, 64],
#		["Ofast", "avx512", 32, 32, 32, 32],
#		["Ofast", "avx512", 32, 256, 256, 256],
#		["Ofast", "avx512", 16, 16, 16, 16],
#		['O3', 'avx', 32, 256, 4, 8]
	]
	T0 = 100
	n_iter = [100]
	n_tunnels = 2

	for S0 in S0_list:
		E_tunnel = 0

		for i in range(n_tunnels):
			print("Run", i)
			t0 = time.time()
			S_best, E_best, S_list, E_list = tunneling_sa(n1, n2, n3, S0, T0, decay_geometric, n_iter[i], E_tunnel, cost_average)
			t = time.time() - t0

			print()
			print("Best solution:", S_best, "with", E_best, "Gflops")
			print("Time:", t)
			print("===")
			print(E_list)
			print(S_list)
			print()

			E_tunnel = max(E_tunnel, E_best)
			S0 = S_best

