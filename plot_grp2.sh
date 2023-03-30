#!/bin/bash

CSV_FILE="$1"
shift
BASEDIR=$(dirname $(realpath $0))

#source $ONEAPI_ROOT/intelpython/latest/bin/activate

#CONDA_ENV_LATEST=$(conda env list | awk '/^20/{print $1}' | sort -n | tail -n 1)
#conda activate $CONDA_ENV_LATEST

mv $CSV_FILE $BASEDIR/current_csv.csv
#####mv $CSV_FILE /opt/cpu_monitor/scripts/current_csv.csv #KEEP!


#$BASEDIR/plot_grp2.py $CSV_FILE
