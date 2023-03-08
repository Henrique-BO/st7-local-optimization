#---------------------------------------------------------------
# S. Vialle
# February 2023
# Altered and developed by Sneha Shakya and Yahya El Fataoui
#---------------------------------------------------------------

import subprocess
import os
import time
ISO3DFD_DIR = os.path.expanduser("~") + "/iso3dfd-st7"

def make(Olevel, simd):
	"""
	Compiles the iso3dfd code
	"""
	filename = f"iso3dfd_dev13_cpu_{simd}_{Olevel}.exe"
	if not os.path.exists("./bin/" + filename):
		# Make command
		cmd = f"make Olevel=-{Olevel} simd={simd} last"
		print("Running command:", cmd)
		res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, cwd=ISO3DFD_DIR)

		# Copy the executable
		cmd = f"cp {ISO3DFD_DIR}/bin/iso3dfd_dev13_cpu_{simd}.exe ./bin/{filename}"
		print("Runing command:", cmd)
		res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
#	else:
#		print("Configuration already exists")
	return filename


def run_iso3dfd(NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block,filename):
        cmd = "bin/"+filename+" 256 256 256 "+str(NbTh)+" 100 "+str(n1_thrd_block)+\
                " "+str(n2_thrd_block)+" "+str(n3_thrd_block)+" > output.txt"
#        print("Executed command: " + cmd)
#        print("---->")
        res = subprocess.run(cmd,shell=True,stdout=subprocess.PIPE)


def parse_output():
	with open('output.txt', 'r') as f:
		for line in f:
			if 'throughput:' in line:
				a = float(line.split()[1])
				cmd = "rm ./output.txt"
#				res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
#				print("Running command:", cmd)
				return a

def run(params):
	Olevel = params[0]
	simd = params[1]
	NbTh = params[2]
	n1_thrd_block = params[3]
	n2_thrd_block = params[4]
	n3_thrd_block = params[5]

	filename = make(Olevel, simd)
	run_iso3dfd(NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block, filename)
	throughput = parse_output()
	return throughput

def neighborhood(params):
	Olevel = params[0]
	simd = params[1]
	NbTh = params[2]
	n1_thrd_block = params[3]
	n2_thrd_block = params[4]
	n3_thrd_block = params[5]

	neighbors = []

	# Olevel
	if Olevel == "O3":
		neighbors.append(["Ofast", simd, NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])
	elif Olevel == "Ofast":
		neighbors.append(["O3", simd, NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])

	# simd
	if simd == "avx":
		neighbors.append([Olevel, "avx2", NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])
		neighbors.append([Olevel, "avx512", NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])
		neighbors.append([Olevel, "sse", NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])
	elif simd == "avx2":
		neighbors.append([Olevel, "avx", NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])
		neighbors.append([Olevel, "avx512", NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])
		neighbors.append([Olevel, "sse", NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])
	elif simd == "avx512":
		neighbors.append([Olevel, "avx2", NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])
		neighbors.append([Olevel, "avx", NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])
		neighbors.append([Olevel, "sse", NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])
	elif simd == "sse":
		neighbors.append([Olevel, "avx2", NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])
		neighbors.append([Olevel, "avx512", NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])
		neighbors.append([Olevel, "avx", NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])

	# NbTh
	if NbTh > 1:
		neighbors.append([Olevel, simd, NbTh - 1, n1_thrd_block, n2_thrd_block, n3_thrd_block])
	if NbTh < 32:
		neighbors.append([Olevel, simd, NbTh + 1, n1_thrd_block, n2_thrd_block, n3_thrd_block])

	# n1_thrd_block
	if n1_thrd_block > 16:
		neighbors.append([Olevel, simd, NbTh, int(n1_thrd_block / 2), n2_thrd_block, n3_thrd_block])
	if n1_thrd_block < 256:
		neighbors.append([Olevel, simd, NbTh, n1_thrd_block * 2, n2_thrd_block, n3_thrd_block])

	# n2_thrd_block
	if n2_thrd_block > 1:
		neighbors.append([Olevel, simd, NbTh, n1_thrd_block, int(n2_thrd_block / 2), n3_thrd_block])
	if n2_thrd_block < 256:
		neighbors.append([Olevel, simd, NbTh, n1_thrd_block, n2_thrd_block * 2, n3_thrd_block])
	# n3_thrd_block
	if n3_thrd_block > 1:
		neighbors.append([Olevel, simd, NbTh, n1_thrd_block, n2_thrd_block, int(n3_thrd_block / 2)])
	if n3_thrd_block < 256:
		neighbors.append([Olevel, simd, NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block * 2])

	return neighbors

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
        L_neigh=neighborhood(S_best)
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
                        L_neigh=neighborhood(S_best)
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
        L_neigh=neighborhood(S_best)
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
                        L_neigh=neighborhood(S_best)
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
