#!/bin/bash

for x in $@; do
    TMP=`mktemp` && cat $x | sed "s/NimbusSanL-Regu/NimbusSanL/g" | sed "s/Helvetica/NimbusSan/g" > $TMP && mv $TMP $x;
done;

