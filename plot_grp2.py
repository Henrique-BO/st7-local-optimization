#!/usr/bin/env python3
## ===============================================================================
##  Copyright 2001-2022 Intel Corporation.
## 
##  This software and the related documents are Intel copyrighted  materials,  and
##  your use of  them is  governed by the  express license  under which  they were
##  provided to you (License).  Unless the License provides otherwise, you may not
##  use, modify, copy, publish, distribute,  disclose or transmit this software or
##  the related documents without Intel's prior written permission.
## 
##  This software and the related documents  are provided as  is,  with no express
##  or implied  warranties,  other  than those  that are  expressly stated  in the
##  License.
## ===============================================================================
## version 2301.1
## ===============================================================================

import tempfile
import argparse
import math
import time
import sys
import os

def output_analysis(file_desc, string):
    file_desc.write(bytes(string, 'utf-8'))
    print(string,end='')

def install_and_import(package):
    import importlib
    try:
        importlib.import_module(package)
    except ImportError:
        print('Install module {}'.format(package))
        import pip
        pip.main(['install', package])
    finally:
        print('Import module {}'.format(package))
        globals()[package] = importlib.import_module(package)

for package in ['matplotlib', 'pandas', 'numpy', 'scipy', 'openpyxl', 'xlsxwriter', 'xlrd']:
    install_and_import(package)

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
import numpy as np
from scipy import stats
from zipfile import ZipFile

tic = time.perf_counter()

parser = argparse.ArgumentParser(description='Parse and plot cpu_monitor data.')
parser.add_argument('--freq', type=int, nargs=2)
parser.add_argument("filename")
args = parser.parse_args()

filepath = os.path.abspath(args.filename)
filepath_wosuffix = os.path.splitext(filepath)[0]
filename_wosuffix = os.path.basename(filepath_wosuffix)
dirpath = os.path.dirname(filepath)

fo = open(os.path.join(dirpath,filename_wosuffix+'.anl'), "wb")

output_analysis(fo, 'CPUMON_CMDLINE: {}\n'.format(os.getenv('CPUMON_CMDLINE')))
output_analysis(fo, 'CPUMON_APPNAME: {}\n'.format(os.getenv('CPUMON_APPNAME')))

substring_count = 0
appargs = ''
comment = ''
if "CPUMON_APPNAME" in os.environ:
    substring_count += 1
    appname = os.getenv('CPUMON_APPNAME')
if "CPUMON_APPARGS" in os.environ:
    substring_count += 1
    appargs = os.getenv('CPUMON_APPARGS')
if "CPUMON_COMMENT" in os.environ:
    substring_count += 1
    comment = '\n\nComment: {}'.format(os.getenv('CPUMON_COMMENT'))

output_analysis(fo, 'CPUMON_APPARGS: {}\n'.format(appargs))
output_analysis(fo, 'CPUMON_COMMENT: {}\n'.format(comment))

print('matplotlib version {}'.format(matplotlib.__version__))

plt.rcParams['axes.labelsize'] = 8
plt.rcParams['axes.titlesize'] = 8
plt.rcParams['lines.linewidth'] = 0.75
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8
plt.xticks(fontsize=6)

##  0: TIME
##  1: PW_PKG0
##  2: PW_DRAM0
##  3: UNCORE_FREQ0
##  4: UNCORE_VOLT0
##  5: TEMP_PKG0
##  6: PW_PKG1
##  7: PW_DRAM1
##  8: UNCORE_FREQ1
##  9: UNCORE_VOLT1
## 10: TEMP_PKG1

## read csv, remove first roz and filter PW_ value to remove bad values from counter overflow
idx = pd.Index([],dtype='int64')

df = pd.read_csv(filepath,sep=';')
df = df.iloc[1: , :]

sub_df = df.filter(regex=("^PW_*"))
(max_row, max_col) = sub_df.shape
for i in range(0, max_col):
    idx = idx.union(sub_df[sub_df.iloc[:,i]>8000.0].index)
df.drop(idx, inplace=True)
print('filter out {} rows'.format(idx.size))
    
(max_row, max_col) = df.shape
print('row: {}, col: {}'.format(max_row,max_col))
df[df.select_dtypes(include=[np.number]).ge(0).all(1)]
print('row: {}, col: {}'.format(max_row,max_col))

if 'MEM_USED' in df.columns:
    mem_used     = df['MEM_USED']
    mem_free     = df['MEM_FREE']
    mem_consumed = df['MEM_CONSUMED']

power_pkg_table   = df.filter(regex=("^PW_PKG[0-9]*"))
power_dram_table  = df.filter(regex=("^PW_DRAM[0-9]*"))
uncore_freq_table = df.filter(regex=("^UNCORE_FREQ[0-9]*"))
uncore_volt_table = df.filter(regex=("^UNCORE_VOLT[0-9]*"))
temp_pkg_table    = df.filter(regex=("^TEMP_PKG[0-9]*"))

power_row, power_col = power_pkg_table.shape
pkg = power_col

core_freq_table   = df.filter(regex=("^CORE[0-9]*_F"))
core_volt_table   = df.filter(regex=("^CORE[0-9]*_V"))

f_row, f_col      = core_freq_table.shape
v_row, v_col      = core_volt_table.shape

df.rename(columns={ df.columns[max_col-1]: "CORE_MEDIAN" }, inplace = True)
df['CORE_MEDIAN'] = core_freq_table.median(axis=1)

### REPORT ANALYSIS
print(df.head())

output_analysis(fo, '')
data_block = core_freq_table.to_numpy()
f_med = np.median(data_block)

output_analysis(fo, '======== Frequency analysis =========\n')
output_analysis(fo, '.........Min: {:6.1f} MHz\n'.format(data_block.min()))
output_analysis(fo, '.........Max: {:6.1f} MHz\n'.format(data_block.max()))
output_analysis(fo, '.....Average: {:6.1f} MHz\n'.format(data_block.mean()))
output_analysis(fo, '......Median: {:6.1f} MHz <<<\n'.format(f_med))
output_analysis(fo, '=====================================\n')

output_analysis(fo, '\n')
output_analysis(fo, '===== Uncore Frequency analysis =====\n')
output_analysis(fo, '              ')
for i in range(0, power_col):
    output_analysis(fo, '   Pkg{}      '.format(i))
output_analysis(fo, '\n')
output_analysis(fo, '.........Min: ')
for i in range(0, power_col):
    output_analysis(fo, '{:7.1f} MHz  '.format(uncore_freq_table.iloc[:,i].min()))
output_analysis(fo, '\n');
output_analysis(fo, '.........Max: ')
for i in range(0, power_col):
    output_analysis(fo, '{:7.1f} MHz  '.format(uncore_freq_table.iloc[:,i].max()))
output_analysis(fo, '\n');
output_analysis(fo, '.....Average: ')
for i in range(0, power_col):
    output_analysis(fo, '{:7.1f} MHz  '.format(uncore_freq_table.iloc[:,i].mean()))
output_analysis(fo, '\n');
output_analysis(fo, '......Median: ')
for i in range(0, power_col):
    output_analysis(fo, '{:7.1f} MHz  '.format(uncore_freq_table.iloc[:,i].median()))
output_analysis(fo, '\n');
output_analysis(fo, '=====================================\n')

output_analysis(fo, '\n')
output_analysis(fo, '========== power analysis ===========\n')
output_analysis(fo, '              ')
for i in range(0, power_col):
    output_analysis(fo, ' Pkg{}    '.format(i))
output_analysis(fo, '\n')
output_analysis(fo, '.........Min: ')
for i in range(0, power_col):
    output_analysis(fo, '{:7.1f} W'.format(power_pkg_table.iloc[:,i].min()))
output_analysis(fo, '\n');
output_analysis(fo, '.........Max: ')
for i in range(0, power_col):
    output_analysis(fo, '{:7.1f} W'.format(power_pkg_table.iloc[:,i].max()))
output_analysis(fo, '\n');
output_analysis(fo, '.....Average: ')
for i in range(0, power_col):
    output_analysis(fo, '{:7.1f} W'.format(power_pkg_table.iloc[:,i].mean()))
output_analysis(fo, '\n');
output_analysis(fo, '......Median: ')
for i in range(0, power_col):
    output_analysis(fo, '{:7.1f} W'.format(power_pkg_table.iloc[:,i].median()))
output_analysis(fo, '\n');
output_analysis(fo, '=====================================\n')

output_analysis(fo, '\n')
output_analysis(fo, '============ Voltage analysis =============\n')
output_analysis(fo, '              ')
for i in range(0, power_col):
    output_analysis(fo, '  Pkg{}   '.format(i))
output_analysis(fo, '  Cores    \n')
output_analysis(fo, '.........Min: ')
for i in range(0, power_col):
    output_analysis(fo, '{:7.3f} v'.format(uncore_volt_table.iloc[:,i].min()))
output_analysis(fo, '{:7.3f} v'.format(core_volt_table.min().min()))
output_analysis(fo, '\n');
output_analysis(fo, '.........Max: ')
for i in range(0, power_col):
    output_analysis(fo, '{:7.3f} v'.format(uncore_volt_table.iloc[:,i].max()))
output_analysis(fo, '{:7.3f} v'.format(core_volt_table.max().max()))
output_analysis(fo, '\n');
output_analysis(fo, '.....Average: ')
for i in range(0, power_col):
    output_analysis(fo, '{:7.3f} v'.format(uncore_volt_table.iloc[:,i].mean()))
output_analysis(fo, '{:7.3f} v'.format(core_volt_table.to_numpy().mean()))
output_analysis(fo, '\n');
output_analysis(fo, '......Median: ')
for i in range(0, power_col):
    output_analysis(fo, '{:7.3f} v'.format(uncore_volt_table.iloc[:,i].median()))
output_analysis(fo, '{:7.3f} v'.format(core_volt_table.median().median()))
output_analysis(fo, '\n');
output_analysis(fo, '===========================================\n')

fo.close()

### WRITE INTO EXCEL FILE
print('Write xlsx file')
sheetname = filename_wosuffix
writer = pd.ExcelWriter(os.path.join(dirpath,filename_wosuffix+'.xlsx'), engine='xlsxwriter')
df.to_excel(writer, sheet_name=sheetname)
workbook  = writer.book
worksheet = writer.sheets[sheetname]
header_format = workbook.add_format({
        'rotation': 90,
        'bold': False,
        'text_wrap': False,
        'align': 'center',
        'valign': 'center',
        'fg_color': 'yellow',
        'border': 1})
for col, value in enumerate(df.columns.values):
    worksheet.write(0, col + 1, value, header_format)

chart = workbook.add_chart({
    'type': 'scatter', 
    'subtype': 'straight' 
})
chart.set_title({'none': True})
for i in range(0,power_col):
    col = 2+5*i
    chart.add_series({
        'name': [sheetname, 0, col],
        'categories': [sheetname, 1, 1, max_row, 1],
        'values': [sheetname, 1, col, max_row, col],
    })
chart.set_x_axis({
    'name': 'runtime (sec)',
    'major_gridlines': {
        'visible': True,
        'line': {'dash_type': 'dash'}
    }
})
chart.set_y_axis({
    'name': 'Power',
    'major_gridlines': {'visible': True}
})
chart.set_legend({'position': 'top'})
worksheet.insert_chart(1, 3, chart)

chart = workbook.add_chart({
    'type': 'scatter', 
    'subtype': 'straight' 
})
chart.set_title({'none': True})
for i in range(0,power_col):
    col = 6+5*i
    chart.add_series({
        'name': [sheetname, 0, col],
        'categories': [sheetname, 1, 1, max_row, 1],
        'values': [sheetname, 1, col, max_row, col],
    })
chart.set_x_axis({
    'name': 'runtime (sec)',
    'major_gridlines': {
        'visible': True,
        'line': {'dash_type': 'dash'}
    }
})
chart.set_y_axis({
    'name': 'Temperature (deg)',
    'major_gridlines': {'visible': True}
})
chart.set_legend({'position': 'top'})
worksheet.insert_chart(1, 11, chart)

chart = workbook.add_chart({
    'type': 'scatter', 
    'subtype': 'straight' 
})
chart.set_title({'none': True})
chart.add_series({
        'name': [sheetname, 0, max_col],
        'categories': [sheetname, 1, 1, max_row, 1],
        'values': [sheetname, 1, max_col, max_row, max_col],
        })
for i in range(0,power_col):
    col = 4+5*i
    chart.add_series({
            'name': [sheetname, 0, col],
            'categories': [sheetname, 1, 1, max_row, 1],
            'values': [sheetname, 1, col, max_row, col],
            'line':   {'width': 1.25, 'dash_type': 'dash'},
            })

worksheet.write_column(1, max_col+2, [ df['TIME'].to_numpy().min(), df['TIME'].to_numpy().max() ])
worksheet.write_column(1, max_col+3, [ f_med, f_med ])
chart.add_series({
        'name': '{:.1f}MHz'.format(f_med),
        'categories': [sheetname, 1, max_col+2, max_row, max_col+2],
        'values': [sheetname, 1, max_col+3, max_row, max_col+3],
        'line':   { 'color': 'orange', 'width': 1.25},
        })

chart.set_x_axis({
    'name': 'runtime (sec)',
    'major_gridlines': {
        'visible': True,
        'line': {'dash_type': 'dash'}
    }
})
chart.set_y_axis({
    'name': 'Frequency (MHz)',
    'major_gridlines': {'visible': True}
})
chart.set_legend({'position': 'top'})
worksheet.insert_chart(17, 3, chart, {'x_scale': 2, 'y_scale': 1.5})

writer.close()


t   = df['TIME'].to_numpy()
t_min = np.min(t)
t_max = np.max(t)

afc = df['CORE_MEDIAN'].to_numpy()

f = plt.figure()
f.set_size_inches(8.27, 11.69*5.0/4.0)
f.suptitle(filepath)

gs = gridspec.GridSpec(6, 2, hspace=.25)

## 0 ######################################################################################
###### Power

dram_energy = 0.0 
pkg_energy = 0.0 
for i in range(0, power_col):
    dram_energy += np.trapz(power_dram_table.iloc[:,i].to_numpy(),t)/1000.0
    pkg_energy += np.trapz(power_pkg_table.iloc[:,i].to_numpy(),t)/1000.0

string = 'PKG Domain Energy: {:.1f}kJ ({:1g}kWatt.h), DRAM Domain Energy: {:.1f}kJ ({:1g}kWatt.h)'.format(pkg_energy,pkg_energy/3600.0,dram_energy,dram_energy/3600.0)

ax = f.add_subplot(gs[0, :])
ax.title.set_text(string)
for i in range(0, power_col):
    ax.plot(t, power_pkg_table.iloc[:,i].to_numpy(), label='PKG{}'.format(i), drawstyle='steps')
    ax.plot(t, power_dram_table.iloc[:,i].to_numpy(), label='DRAM{}'.format(i), drawstyle='steps', ls='dashed')
ax.set_xlabel('Runtime (sec)')
ax.set_ylabel('RAPL Power (Watt)')
ax.set_ylim(0,420)
ax.legend(prop={"size":8})
ax.minorticks_on()
ax.grid(True, which='major', linestyle='--', linewidth=0.25)
ax.grid(True, which='minor', linestyle=':', linewidth=0.25)

## 1 ######################################################################################
###### Memory utilization
ax = f.add_subplot(gs[1, :])
if 'MEM_USED' in df.columns:
    ax.plot(t, mem_used.to_numpy()/1024., label='used', ls='dashed', drawstyle='steps')
    ax.plot(t, mem_free.to_numpy()/1024., label='free', ls='dashed', drawstyle='steps')
    ax.plot(t, mem_consumed.to_numpy()/1024., label='consumed', drawstyle='steps')
    ax.legend(prop={"size":8})
else:
    ax.text(0.5, 0.5, r'No data',
            horizontalalignment='center',
            verticalalignment='center',
            fontsize=15, color='red',
            rotation=45,
            transform=ax.transAxes)
ax.set_xlabel('Runtime (sec)')
ax.set_ylabel('Memory (GiBytes)')
ax.minorticks_on()
ax.grid(True, which='major', linestyle='--', linewidth=0.25)
ax.grid(True, which='minor', linestyle=':',  linewidth=0.25)

## 2 ######################################################################################
###### Temperature 
ax = f.add_subplot(gs[2,:])
for i in range(0, power_col):
    ax.plot(t, temp_pkg_table.iloc[:,i].to_numpy(), label='PKG{}'.format(i),drawstyle='steps')
ax.set_xlabel('Runtime (sec)')
ax.set_ylabel('Package temperature (°C)')
ax.legend(prop={"size":8})
ax.minorticks_on()
ax.grid(True, which='major', linestyle='--', linewidth=0.25)
ax.grid(True, which='minor', linestyle=':', linewidth=0.25)

## 3 ######################################################################################
###### Frequency 
ax = f.add_subplot(gs[3, :])
string = 'Median frequency: {:.1f}MHz '.format(f_med)
ax.set_title(string, loc='left')
for i in range(0, power_col):
    ax.plot(t, uncore_freq_table.iloc[:,i].to_numpy(), label='UNCORE_FREQ{}'.format(i), linestyle='dashed', linewidth=1)
for i in range(0, f_col):
    col_name = core_freq_table.columns[i]
    if i<4:
        ax.plot(t, core_freq_table.iloc[:,i].to_numpy(), label=col_name, linewidth=0.5, drawstyle='steps')
    else:
        ax.plot(t, core_freq_table.iloc[:,i].to_numpy(), linewidth=0.5, drawstyle='steps')

ax.plot(t, afc, 'k-', label='MEDIAN_CORE_FREQ', linewidth=1)
ax.plot([t_min, t_max], [f_med, f_med], linestyle='dashed', color='green', linewidth=1)
ax.fill_between(t, afc-100, afc+100, alpha=0.2)
ax.set_xlabel('Runtime (sec)')
ax.set_ylabel('Frequency (MHz)')

if args.freq:
    ax.set_ylim(args.freq)
ax.legend(prop={"size":6})
ax.minorticks_on()
ax.grid(True, which='major', linestyle='--', linewidth=0.25)
ax.grid(True, which='minor', linestyle=':', linewidth=0.25)

## 4 ######################################################################################
###### Voltage 
ax = f.add_subplot(gs[4, :])
for i in range(0, v_col):
    ax.plot(t, core_volt_table.iloc[:,i].to_numpy(), linewidth=0.5, drawstyle='steps')

ax.set_xlabel('Runtime (sec)')
ax.set_ylabel('Voltage (V)')

ax.minorticks_on()
ax.grid(True, which='major', linestyle='--', linewidth=0.25)
ax.grid(True, which='minor', linestyle=':', linewidth=0.25)

## 5:0 ######################################################################################
###### Histogram 
vector = np.reshape(core_freq_table.to_numpy(),-1)

x_min = math.floor(min(vector)/100)*100
x_max = math.ceil(max(vector)/100)*100

if x_min==x_max:
    x_min = x_min-100
    x_max = x_max+100

ax = f.add_subplot(gs[5, 0], frameon=False)
ax.hist(vector, align='mid', bins=range(x_min,x_max,50))
ax.axvline(f_med, color='k', linestyle='dashed', linewidth=1)
min_ylim, max_ylim = plt.ylim()
ax.text(f_med*1.1, max_ylim*0.9, 'f_med: {:.1f}MHz'.format(f_med), fontsize=8)
ax.tick_params(axis='x', labelrotation=90, labelsize=4)
ax.set_xticks(range(x_min, x_max, 100))
ax.set_xlabel('Frequency bins')

## 5:1 ######################################################################################
##### Frequency map
ax = f.add_subplot(gs[5, 1], frameon=False)
ax.set_xmargin(0)
core_list = core_freq_table.columns.to_numpy()

if f_col>1:
    h, bins = np.histogram(core_freq_table[core_list[0]].to_numpy() , bins=range(x_min,x_max,50))
    h = h/np.sum(h)
    for i in range(1, f_col):
        temp, bins = np.histogram( core_freq_table[core_list[i]].to_numpy() , bins=range(x_min,x_max,50))
        h = np.vstack((h, temp/np.sum(temp))) 
    c = ax.pcolormesh(bins, range(0, f_col+1), h, vmin=h.min(), vmax=h.max())
    ax.axvline(f_med, color='white', linestyle='dashed')
    ax.tick_params(axis='x', labelrotation=90, labelsize=5)
    ax.set_xticks(range(x_min, x_max, 100))
    f.colorbar(c, ax=ax)
else:
    ax.text(0.5, 0.5, r'No data',
        horizontalalignment='center',
        verticalalignment='center',
        fontsize=15, color='red',
        rotation=45,
        transform=ax.transAxes)

ax.set_xlabel('Frequency bins')
ax.set_ylabel('Core id#')

if substring_count>0:
    plt.figtext(0.5, 0.0275, appname+' '+appargs+comment,
        ha='center', fontsize=6,  family='Monospace', 
        bbox={"facecolor":"orange", "alpha":0.85, "pad":20},
        wrap=True)

plt.show()

##  
f.savefig(os.path.join(dirpath,filename_wosuffix+'.pdf'))
f.savefig(os.path.join(dirpath,filename_wosuffix+'.png'))
##

print('\nBuild zip package ...')

zipname = os.path.join(dirpath,filename_wosuffix+'.zip')
if os.path.exists(zipname):
    print('{} exist... remove it.'.format(zipname))
    os.remove(zipname)

tempname = next(tempfile._get_candidate_names())
path_size_max = len(filepath)+2
with ZipFile(tempname, 'w') as zipObj:
    for filename in os.listdir(dirpath):
        filename = os.path.join(dirpath,filename)
        if os.path.basename(filename).startswith(filename_wosuffix+'.'):
            filestats = os.stat(filename)
            print(f'+    ADD   {filename:<{path_size_max}} - {filestats.st_size:10d} Bytes')
            zipObj.write(os.path.abspath(filename), os.path.basename(filename))
os.rename(tempname, zipname)
filestats = os.stat(zipname)
print(f'= zipfile: {zipname:<{path_size_max}} - {filestats.st_size:10d} Bytes')

toc = time.perf_counter()
print()
print(f"{toc - tic:0.4f} seconds")
print(zipname)

# Local variables:
# mode: python
# sh-basic-offset: 4
