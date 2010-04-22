#!/bin/bash
cp $$(find texmf/ | grep -v svn | grep "\.") .
echo "Done."
