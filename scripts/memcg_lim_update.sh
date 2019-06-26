#!/bin/bash

# This script discards processes from memcg limit subgroup except core process.

if [ $# -ne 1 ]
then
	echo "Usage: $0 <pid of core process>"
	exit 1
fi

PID=$1

MEMCG_ORIG_DIR=/sys/fs/cgroup/memory
MEMCG_DIR=/sys/fs/cgroup/memory/run_memcg_lim_$USER

pids=`cat $MEMCG_DIR/tasks`

children=`ls /proc/$PID/task`

for pid in $pids
do
	ischild=`echo $children | grep $pid | wc -l`
	if [ $ischild -eq 0 ]
	then
		echo $pid >> $MEMCG_ORIG_DIR/tasks
	fi
done
