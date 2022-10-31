# FJSP-SMT2020-multishot

This work investigates solving semiconductor manufacturing scheduling tasks using Answer Set Programming (ASP). We tested our work (in progress) with small examples derived from the SMT2020 dataset.

- The following features have been considered in this work:
    - Machine Maintenance
    - Machine Setup
    - Machine Assignment (Flexible/Fixed)
- Our main objectives are to minimize the total completion time (makespan) of schedules and the machine-setup changes.

This repository includes the following files/folders:

<table>
<tr><th>File/Folder</th><th>Description</th></tr>
<tr><td style="font-family:'Courier New'">README.md</td><td>this file</td></tr>
<tr><td style="font-family:'Courier New'">encoding_msw_multi-shot.lp</td><td>main scheduling encoding</td></tr>
<tr><td style="font-family:'Courier New'">parsing.lp</td><td>auxiliary rules to reformat facts (included by <span style="font-family:'Courier New'">encoding_msw_multi-shot.lp</span>)</td></tr>
<tr><td style="font-family:'Courier New'">machine_selection.lp</td><td>auxiliary rules to analyze machine groups (included by <span style="font-family:'Courier New'">encoding_msw_multi-shot.lp</span>)</td></tr>
<tr><td style="font-family:'Courier New'">instances</td><td>instance files for testing</td></tr>
</table>

## Usage

Our scheduling encoding and instances can be run with [Clingo[DL]](https://potassco.org/labs/clingodl/) as illustrated by the following example calls.

We have two python versions for different packages:

- Package[5.5.2]
	- Fixed machine assignment:
        - ``python dlO_multi-obj.py encoding_msw_multi-shot.lp instances/instance04.lp``

	- Flexible machine assignment:
        - ``python dlO_multi-obj.py encoding_msw_multi-shot.lp instances/instance04.lp --const flex=1``

- Package[5.5.0]
	- Fixed machine assignment:
        - ``python dlO_5.5.0_multi-obj.py encoding_msw_multi-shot.lp instances/instance04.lp``

	- Flexible machine assignment:
        - ``python dlO_5.5.0_multi-obj.py encoding_msw_multi-shot.lp instances/instance04.lp --const flex=1``

