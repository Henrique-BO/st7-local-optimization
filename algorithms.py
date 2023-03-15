import random
import math
import time

from common import Algorithm
from common import run, neighborhood


class Greedy(Algorithm):

	name = "ghc"
	full_name = "Greedy Hill Climbing"

	def __init__(self, n1, n2, n3, S0, k_max):
		super().__init__(n1, n2, n3, S0, k_max)

	def optimize(self):
		time0 = time.time()
		self.print_params()

		S_best = self.S0
		E_best = cost(S_best)
		L_neigh = neighborhood(S_best, self.n1, self.n2, self.n3)

		S_list = [S_best]
		E_list = [E_best]

		k = 0
		NewBetterS = True
		while(k < k_max and NewBetterS):
			S = L_neigh.pop()
			E = self.cost(S)
			for S_prime in L_neigh:
				E_prime = self.cost(S_prime)
				if E_prime > E:
					S = S_prime
					E = E_prime
			if E > E_best:
				S_best = S
				E_best = E
				L_neigh = neighborhood(S_best, self.n1, self.n2, self.n3)
			else:
				NewBetterS = False
			k = k + 1
			print('k: ', k)
			S_list.append(S)
			E_list.append(E)
		
		self.S_best = S_best
		self.E_best = E_best
		self.S_list = S_list
		self.E_list = E_list
		self.runtime = time.time() - time0


class ParallelGreedy(Algorithm):

	name = "pghc"
	full_name = "Parallel Greedy Hill Climbing"

	def __init__(self, n1, n2, n3, S0, k_max):
		super().__init__(n1, n2, n3, S0, k_max)

	def optimize(self):
		time0 = time.time()
		self.print_params()

		S_best = self.S0
		TabE = []
		E_best = self.cost(S_best)
		S_list = [S_best]
		E_list = [E_best]
		L_neigh=neighborhood(S_best, self.n1, self.n2, self.n3)
		#print("L_eigh:", L_neigh)
		k=0
		NewBetterS=True
		while(k<k_max and NewBetterS):
			for i in range(len(L_neigh)):
				#print("L_neigh[i]: ", L_neigh[i])
				TabE.append(cost(L_neigh[i]))
				#print(i,": ", TabE[i])
			j = 0
			for i in range(len(L_neigh)):
				if TabE[i] > TabE[j]:
					j = i
			E=TabE[j]
			S=L_neigh[j]
			if E>E_best:
				S_best=S
				E_best=E
				L_neigh=neighborhood(S_best, self.n1, self.n2, self.n3)
			else:
				NewBetterS=False
			k=k+1
			S_list.append(S)
			E_list.append(E)
		
		self.S_best = S_best
		self.E_best = E_best
		self.S_list = S_list
		self.E_list = E_list
		self.runtime = time.time() - time0
		

class SimulatedAnnealing(Algorithm):

	name = "sa"
	full_name = "Simulated Annealing"

	def __init__(self, n1, n2, n3, S0, k_max, T0, temp_decay):
		super().__init__(n1, n2, n3, S0, k_max)

		self.T0 = T0
		self.params["T0"] = T0

		self.params["temp_decay"] = temp_decay
		if temp_decay == "linear":
			self.temp_decay = self.decay_linear
		elif temp_decay == "geometric":
			self.temp_decay = self.decay_geometric
		else:
			raise ValueError("Invalid temp_decay")

	def decay_geometric(self, k):
		a = 10**(math.log10(0.01)/self.k_max)
		return (a**k)*self.T0

	def decay_linear(self, k):
		return self.T0*(1 - k/self.k_max)

	def optimize(self):
		time0 = time.time()
		self.print_params()

		S_best = self.S0
		E_best = self.cost(self.S0)
		S = self.S0
		E = E_best
		neighbors = neighborhood(self.S0, self.n1, self.n2, self.n3)
		T = self.T0
		
		S_list = [S_best]
		E_list = [E_best]

		for k in range(self.k_max):
			S_new = random.choice(neighbors)
			E_new = self.cost(S_new)
			print(f"[{k}/{self.k_max}] {S_new} {E_new}", end='')
			if E_new > E or random.random() < math.exp(-(E-E_new)/T):
				S = S_new
				E = E_new
				neighbors = neighborhood(S, self.n1, self.n2, self.n3)
				if E > E_best:
					S_best = S
					E_best = E
				print(" ACCEPTED")
			else:
				print(" REJECTED")
			T = self.temp_decay(k)
			
			S_list.append(S)
			E_list.append(E)
		
		self.S_best = S_best
		self.E_best = E_best
		self.S_list = S_list
		self.E_list = E_list
		self.runtime = time.time() - time0


class TabuSA(SimulatedAnnealing):

	name = "tabu_sa"
	full_name = "Tabu Simulated Annealing"

	def __init__(self, n1, n2, n3, S0, k_max, T0, temp_decay, tabu_size):
		super().__init__(n1, n2, n3, S0, k_max, T0, temp_decay)
		
		self.tabu_size = tabu_size
		self.params["tabu_size"] = tabu_size

	def optimize(self):
		time0 = time.time()
		self.print_params()

		S_best = self.S0
		E_best = self.cost(self.S0)
		S = self.S0
		E = E_best
		neighbors = neighborhood(self.S0, self.n1, self.n2, self.n3)
		T = self.T0

		Ltabu = [S_best]

		S_list = [S_best]
		E_list = [E_best]

		for k in range(self.k_max):
			S_new = random.choice(neighbors)
			while S_new in Ltabu:
				S_new = random.choice(neighbors)
			E_new = cost(S_new)
			print(f"[{k}/{self.k_max}] {S_new} {E_new}", end='')
			if E_new > E or random.random() < math.exp(-(E-E_new)/T):
				S = S_new
				E = E_new
				neighbors = neighborhood(S, self.n1, self.n2, self.n3)
				if E > E_best:
					S_best = S
					E_best = E
				Ltabu = fifo_add(S_best, Ltabu, tabu_size)
				print(" ACCEPTED")
			else:
				print(" REJECTED")
			print(Ltabu)
			T = self.temp_decay(k)

			S_list.append(S)
			E_list.append(E)

		self.S_best = S_best
		self.E_best = E_best
		self.S_list = S_list
		self.E_list = E_list
		self.runtime = time.time() - time0


class TunnelingSA(SimulatedAnnealing):

	name = "tunnel_sa"
	full_name = "Tunneling Simulated Annealing"

	def __init__(self, n1, n2, n3, S0, k_max, T0, temp_decay, cost_fun, E_tunnel):
		super().__init__(n1, n2, n3, S0, k_max, T0, temp_decay)
		
		self.params["cost_fun"] = cost_fun
		if cost_fun == "average":
			self.cost = cost_average
		elif cost_fun == "stochastic":
			self.cost = cost_stochastic
		else:
			raise ValueError("Invalid cost_fun")

		self.params["E_tunnel"] = E_tunnel
		self.E_tunnel = E_tunnel

	def cost_average(self, S):
		E = run(S, self.n1, self.n2, self.n3)
		if E < self.E_tunnel:
			return (E + self.E_tunnel)/2, E
		else:
			return E, E

	def cost_stochastic(self, S):
		gamma = 0.004
		E = run(S, self.n1, self.n2, self.n3)
		return math.exp(-gamma*(E_tunnel - E)) - 1, E

	def optimize(self):
		time0 = time.time()
		self.print_params()

		S_best = self.S0
		E_best_tun, E_best = self.cost(self.S0)
		S = self.S0
		E_tun = E_best_tun
		E = E_best
		neighbors = neighborhood(self.S0, self.n1, self.n2, self.n3)
		T = T0

		S_list = [S_best]
		E_list = [E_best]

		for k in range(self.k_max):
			S_new = random.choice(neighbors)
			E_new_tun, E_new  = cost(S_new, E_tunnel, n1, n2, n3)
			print(f"[{k}/{self.k_max}] {S_new} {E_new}", end='')
			if E_new_tun > E_tun or random.random() < math.exp(-(E_tun-E_new_tun)/T):
				S = S_new
				E_tun = E_new_tun
				E = E_new
				neighbors = neighborhood(S, self.n1, self.n2, self.n3)
				if E_tun > E_best_tun:
					S_best = S
					E_best_tun = E_tun
					E_best = E
				print(" ACCEPTED")
			else:
				print(" REJECTED")
			T = self.temp_decay(k)
			
			S_list.append(S)
			E_list.append(E)

		self.S_best = S_best
		self.E_best = E_best
		self.S_list = S_list
		self.E_list = E_list
		self.runtime = time.time() - time0

