#!/bin/bash
cd ~/Owl/modules
# Append to PYTHONPATH if not already in it
export HOWLPATH=/home/josh/Owl
if [ -d "$HOWLPATH" ] && [[ ":$PYTHONPATH:" != *":$HOWLPATH:"* ]]; then
    export PYTHONPATH="${PYTHONPATH:+"$PYTHONPATH:"}$HOWLPATH"
fi
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
