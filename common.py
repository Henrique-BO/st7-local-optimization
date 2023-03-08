#---------------------------------------------------------------
# S. Vialle
# February 2023
#---------------------------------------------------------------

import subprocess
import os
import json
import pandas as pd

ISO3DFD_DIR = os.path.expanduser("~") + "/iso3dfd-st7"
SAVE_DIR = os.path.join(os.getcwd(), "results")

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
		cmd = f"mkdir -p bin && cp {ISO3DFD_DIR}/bin/iso3dfd_dev13_cpu_{simd}.exe ./bin/{filename}"
		print("Runing command:", cmd)
		res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
#	else:
#		print("Configuration already exists")
	return filename


def run_iso3dfd(n1, n2, n3, NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block,filename):
        cmd = "bin/"+filename+" "+str(n1)+" "+str(n2)+" "+str(n3)+" "+str(NbTh)+" 100 "+str(n1_thrd_block)+\
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

def run(params, n1=256, n2=256, n3=256):
	Olevel = params[0]
	simd = params[1]
	NbTh = params[2]
	n1_thrd_block = params[3]
	n2_thrd_block = params[4]
	n3_thrd_block = params[5]

	filename = make(Olevel, simd)
	run_iso3dfd(n1, n2, n3, NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block, filename)
	throughput = parse_output()
	return throughput


def neighborhood(params, n1, n2, n3):
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
	if n1_thrd_block < n1:
		neighbors.append([Olevel, simd, NbTh, n1_thrd_block * 2, n2_thrd_block, n3_thrd_block])

	# n2_thrd_block
	if n2_thrd_block > 1:
		neighbors.append([Olevel, simd, NbTh, n1_thrd_block, int(n2_thrd_block / 2), n3_thrd_block])
	if n2_thrd_block < n2:
		neighbors.append([Olevel, simd, NbTh, n1_thrd_block, n2_thrd_block * 2, n3_thrd_block])
	# n3_thrd_block
	if n3_thrd_block > 1:
		neighbors.append([Olevel, simd, NbTh, n1_thrd_block, n2_thrd_block, int(n3_thrd_block / 2)])
	if n3_thrd_block < n3:
		neighbors.append([Olevel, simd, NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block * 2])

	return neighbors


class Result:
        def __init__(self, id=None):
                self.id = None
                self.json_fn = os.path.join(SAVE_DIR, "summary.json")
                if id != None:
                        self.load_from_id(id)

        def load_from_id(self, id):
                self.id = id
                with open(self.json_fn, "r") as f:
                        summary = json.load(f)
                id_str = str(id)
                self.params = summary[id_str]["params"]
                self.S_best = summary[id_str]["S_best"]
                self.E_best = summary[id_str]["E_best"]
                self.runtime = summary[id_str]["runtime"]

                csv_fn = os.path.join(SAVE_DIR, f"{self.id:05d}.csv")
                self.data = pd.read_csv(csv_fn, index_col=0)

        def set_data(self, params, S_list, E_list, S_best, E_best, runtime):
                self.data = pd.DataFrame(S_list, columns = ["Olevel", "simd", "NbTh", "n1_thrd_block", "n2_thrd_block", "n3_thrd_block"])
                self.data["E"] = E_list
                self.params = params
                self.S_best = S_best
                self.E_best = E_best
                self.runtime = runtime

        def calculate_id(self):
                i = -1
                for name in os.listdir(SAVE_DIR):
                        if name[-4:] == ".csv":
                            i = max(i, int(name[:-4]))
                self.id = i+1

        def save(self):
                if not os.path.exists(SAVE_DIR):
                    subprocess.run(f"mkdir -p {SAVE_DIR}", shell=True, stdout=subprocess.PIPE)
                if self.id == None:
                        self.calculate_id()
                if os.path.exists(self.json_fn):
                        with open(self.json_fn, "r") as f:
                                summary = json.load(f)
                else:
                        summary = {}
                id_str = str(self.id)
                summary[id_str] = {}
                summary[id_str]["params"] = self.params
                summary[id_str]["S_best"] = self.S_best
                summary[id_str]["E_best"] = self.E_best
                summary[id_str]["runtime"] = self.runtime
                print("Saving summary file to", self.json_fn)
                with open(self.json_fn, "w") as f:
                        json.dump(summary, f, indent=4)

                csv_fn = os.path.join(SAVE_DIR, f"{self.id:05d}.csv")
                print("Saving result file to", csv_fn)
                self.data.to_csv(csv_fn)

        def plot(self):
                plt.figure()
                plt.plot(self.data["E"], label=f"{self.id:05d}")
                plt.xlabel("Iteration")
                plt.ylabel("Throughput (MPoints/s)")
                plt.legend()
                plt.grid()

#-----------------------------------------------------------------
# Main code
#-----------------------------------------------------------------

if __name__ == "__main__":
	params = ["Ofast", "avx", 32, 16, 8, 8]
	t = run(params)
	print(t)

	neighbors = neighborhood(params, 256, 256, 256)
	print(neighbors)

	params2 = neighbors[5]
	t = run(params)
	print(t)
