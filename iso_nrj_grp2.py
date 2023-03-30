import pandas as pd
import numpy as np

# This program makes sense of the information in a CSV file, integrates power measurements and outputs 3 energy values into a file called energy_output.txt
def csv_to_energy(csv_path):
        """takes a csv file from cpu_monitor and return the energy consumed"""
        idx = pd.Index([],dtype='int64')

        #delete line in csv
        with open(csv_path,'r') as inp:
            lines = inp.readlines()
            ptr = 1
            with open("Database_edited2.txt",'w') as out:
                for line in lines:
                    if ptr != 3:
                        out.write(line)
                    ptr += 1

        #convert txt to csv
        df = pd.read_csv('Database_edited2.txt')
        df.to_csv('Database_edited2.csv', index=None)
        df = pd.read_csv('Database_edited2.csv',sep=';')

        del df[df.columns[-1]] # to delete last column with null values
        sub_df = df.filter(regex=("^PW_*"))
        (max_row, max_col) = sub_df.shape
        for i in range(0, max_col):
                idx = idx.union(sub_df[sub_df.iloc[:,i].astype(float)>8000.0].index)


        df.drop(idx, inplace=True)
        print('filter out {} rows'.format(idx.size))
        (max_row, max_col) = df.shape
        print('row: {}, col: {}'.format(max_row,max_col))
        df[df.select_dtypes(include=[np.number]).ge(0).all(1)]
        print('row: {}, col: {}'.format(max_row,max_col))

        power_pkg_table = df.filter(regex=("^PW_PKG[0-9]*"))
        power_dram_table = df.filter(regex=("^PW_DRAM[0-9]*"))

        power_row, power_col = power_pkg_table.shape
        pkg = power_col

        t  = df['TIME'].to_numpy()
        t_min = np.min(t)
        t_max = np.max(t)

        dram_energy = 0.0
        pkg_energy = 0.0
        for i in range(0, power_col):
                dram_energy += np.trapz(power_dram_table.iloc[:,i].to_numpy(),t)/1000.0
                pkg_energy += np.trapz(power_pkg_table.iloc[:,i].to_numpy(),t)/1000.0
        return dram_energy,pkg_energy,dram_energy+pkg_energy

dram_energy,pkg_energy,combined = csv_to_energy('/opt/cpu_monitor/scripts/current_csv.csv')

print("DRAM_energy: ",dram_energy)
print("PKG_energy: ",pkg_energy)
print("DRAM_PKG_combined ", combined)

with open('energy_output.txt', 'w') as f:
        f.write(str(dram_energy))
        f.write (" ")
        f.write(str(pkg_energy))
        f.write (" ")
        f.write(str(combined))