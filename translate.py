#!/usr/bin/python3

infile = './.emojis2'
outfile = './.emojis3'

with open(infile,'r') as f1:
    with open(outfile,'w') as f2:
        for line in f1:
            e = line.strip().encode('unicode-escape').decode('utf-8')
            print(e)
            f2.write(e)
            f2.write('\n')
