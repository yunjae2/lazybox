#!/usr/bin/env python2.7

import sys

if len(sys.argv) < 2:
    print "Usage: %s <field name>" % sys.argv[0]
    exit(1)

# example input line is output of `$ perf script`.  It may looks as below.
# command, pid, tid, timestamp, tracepoint name, and trace
#
# memwalk  3837 [012]   383.632199: kmem:mm_page_alloc: \
#           page=0x2f95b76 pfn=49896310 order=0 migratetype=0 \
#           gfp_flags=GFP_NOWAIT|__GFP_NOWARN

wanted = sys.argv[1]

for line in sys.stdin:
    tokens = line.split()
    try:
        time = float(tokens[3][:-1]) * 1000 * 1000 * 1000   # nano second level
    except ValueError:
        # ignore
        continue
    for fields in tokens[5:]:
        key, value = fields.split('=')
        if key == wanted:
            print "%d %s" % (int(time), value)
