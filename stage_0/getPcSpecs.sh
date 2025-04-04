#!/bin/bash -e

#add file
touch pcspecs.txt

#pipe cpu specs into file
cat /proc/cpuinfo > pcspecs.txt
