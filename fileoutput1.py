#---------------------------------------------------------------
# S. Vialle
# February 2023
# Altered and developed by Sneha Shakya and Yahya El Fataoui
#---------------------------------------------------------------

import subprocess
import os
import time

from common import run, neighborhood


#-----------------------------------------------------------------
# Main code
#-----------------------------------------------------------------
def cost(S_0):
	a=0
	for i in range(3):
		a+=run(S_0)
		print('a: ', a, ' i : ', i)
	return a/3

def greedyLocalSearchAlgo(S_0, k_max):
	S_best = S_0
	E_best = cost(S_best)
	L_neigh=neighborhood(S_best, 256, 256, 256)
	k=0

	S_list = [S_best]
	E_list = [E_best]

	NewBetterS=True
	while(k<k_max and NewBetterS):
		S=L_neigh.pop()
		E=cost(S)
		for S_prime in L_neigh:
			E_prime=cost(S_prime)
			if E_prime>E:
				S=S_prime
				E=E_prime
		if E>E_best:
			S_best=S
			E_best=E
			L_neigh=neighborhood(S_best, 256, 256, 256)
		else:
			NewBetterS=False
		k=k+1
		print('k: ', k)
		S_list.append(S)
		E_list.append(E)
	return S_best, E_best, S_list, E_list, k

##print(run_iso3dfd(32, 16, 16, 16, "iso3dfd_dev13_cpu_avx512_Ofast.exe"))
#t0 = time.time()
#S_best, E_best, S_list, E_list, k = greedyLocalSearchAlgo(['Ofast','avx512',32,16,16,16], 100)
#t = time.time() - t0
#print()
#print("===")
#print("Best solution: ", S_best, "with ", E_best, "Mpoints/s")
#print("Time: ", t)
#print("Number of iterations: ", k+1) # adding 1 because k index starts from 0
#print("===")
#print(E_list)
#print(S_list)
#print()

def parallelGreedyLocalSearchAlgo(S_0, k_max):
	S_best = S_0
	TabE = []
	E_best = cost(S_best)
	S_list = [S_best]
	E_list = [E_best]
	L_neigh=neighborhood(S_best, 256, 256, 256)
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
			L_neigh=neighborhood(S_best, 256, 256, 256)
		else:
			NewBetterS=False
		k=k+1
		S_list.append(S)
		E_list.append(E)
	return S_best, E_best, S_list, E_list, k

t0 = time.time()
S_best, E_best, S_list, E_list, k = parallelGreedyLocalSearchAlgo(['Ofast','avx512',32,16,16,16], 100)
t = time.time() - t0
print()
print("===")
print("Best solution: ", S_best, "with ", E_best, "Mpoints/s")
print("Time: ", t)
print("Number of iterations: ", k+1) # adding 1 because k index starts from 0
print("===")
print(E_list)
print(S_list)
print()
