# Semiconductor_scheduling_multi-shot

It contains an encoding of solving Job-shop Scheduling Problem, python api and instances \

- The clingo package(5.6.1):
    - [using optimization call] ``clingo-dl encoding_msw.lp instances\instance01..11.lp --minimize-variable=makespan``
    - [using multi-shot] ``python dlO.py encoding_msw_multi-shot.lp instances\instance01..11.lp``