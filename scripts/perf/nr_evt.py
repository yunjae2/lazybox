# perf script event handlers, generated by perf script -g python
# Licensed under the terms of the GNU GPL License version 2

# The common_* event handler fields are the most useful fields common to
# all events.  They don't necessarily correspond to the 'common_*' fields
# in the format files.  Those fields not available as handler params can
# be retrieved using Python functions of the form common_*(context).
# See the perf-trace-python Documentation for the list of available functions.

import os
import sys
import lbperfutil

def trace_begin():
    pass

def trace_end():
    print "Every Events per Second"
    print "======================="
    print ""
    lbperfutil.pr_evcnts_in_time()

    """
    print "\n"
    print "Event per second"
    print "================"
    print ""
    for ev in sorted(lbperfutil.event_names()):
        lbperfutil.pr_evcnts_in_time([ev])
        print ""
    """

    print "\n"
    print "Total Events Count"
    print "=================="
    print ""
    for ev in sorted(lbperfutil.event_names()):
        print "event ", ev, ": ", lbperfutil.nr_total_event(ev)

# pd is for parameters dict
# keys of pd: attr, symbol, sample, dso, comm, ev_name, raw_buf, callchain
# keys of pd['sample']: ip, pid, period, time, tid, cpu
def process_event(pd):
    name = pd["ev_name"]
    count = pd["sample"]["period"]
    t = pd["sample"]["time"] / (1000*1000*1000)
    lbperfutil.count_event(name, t, count)

#def trace_unhandled(event_name, context, event_fields_dict):
#		print ' '.join(['%s=%s'%(k,str(v))for k,v in sorted(event_fields_dict.items())])

#def print_header(event_name, cpu, secs, nsecs, pid, comm):
#	print "%-20s %5u %05u.%09u %8u %-20s " % \
#	(event_name, cpu, secs, nsecs, pid, comm),
