#---------------------------------------------------------------
# S. Vialle
# February 2023
#---------------------------------------------------------------

import subprocess
import os

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
		cmd = f"mkdir bin && cp {ISO3DFD_DIR}/bin/iso3dfd_dev13_cpu_{simd}.exe ./bin/{filename}"
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
				res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
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

if __name__ == "__main__":
	params = ["Ofast", "avx", 32, 16, 8, 8]
	t = run(params)
	print(t)

	neighbors = neighborhood(params)
	print(neighbors)

	params2 = neighbors[5]
	t = run(params)
	print(t)
