#!/bin/bash
cd ~/howl/modules
./owl.py $*
while [ 1 ]
do
    secs=$((3))

    while [ $secs -gt 0 ]; do
        echo -ne "Restarting in $secs\033[0K\r"
        sleep 1
        : $((secs--))
    done

    ./owl.py -l true $*
done
