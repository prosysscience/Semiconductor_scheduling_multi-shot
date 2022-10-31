#!/usr/bin/python
import sys
import clingo
from clingo import ast
from clingo import Function, Number
from clingodl import ClingoDLTheory
import time


NUM_OF_TIME_WINDOWS = 0
MAX_TIMEOUT = 600
MAX_TIMEOUT_WEAK = 300


class Application(clingo.Application):
    '''
    Application class similar to clingo-dl (excluding optimization).
    '''
    def __init__(self, name):
        self.__theory = ClingoDLTheory()
        self.program_name = name
        self.version = ".".join(str(x) for x in self.__theory.version())

    def register_options(self, options):
        self.__theory.register_options(options)

    def validate_options(self):
        self.__theory.validate_options()
        return True

    def __on_statistics(self, step, accu):
        self.__theory.on_statistics(step, accu)

    def __hidden(self, symbol):
        return symbol.type == clingo.SymbolType.Function and symbol.name.startswith("__")

    # get the Time out per Time Window
    def get_TimeOut(self):
        return MAX_TIMEOUT/(NUM_OF_TIME_WINDOWS + 1), MAX_TIMEOUT_WEAK
    # ************************************************

    # get the assignment of the operations in a string format to be sent as facts for the next Time Window
    def get_total_facts(self, assignment, i):
        start_time = ''
        to_join = []
        for name, value in assignment:
            if str(name) != 'makespan':
                facts_format = 'startTime({},{},{}).'.format(name, value, i)
                to_join.append(facts_format)
            else:
                bound = int(value)
        start_time = ' '.join(to_join)
        return start_time, bound
    # ****************************************************************************************************

    # get the part that should be grounded and solved
    def step_to_ground(self, prg, step):
        string = 'solutionTimeWindow' + str(step)
        parts = []
        if step > 0:
            parts.append(('subproblem', [Number(step)]))
            if step > 1:
                parts.append((string, []))
                prg.add(string, [], self.compressed_start_time)
        else:
            parts.append(('base', []))
        return parts
    # ***********************************************

    # add a new constraint to get lower value of bound (Optimization Part)
    def add_new_constraint(self, prg, bound):
        prg.cleanup()
        prg.ground([('opt', [Number(bound-1)])])
        prg.assign_external(Function('bound', [Number(bound-1)]), True)

    # ground weak constraint with a limitation of the makespan value
    def weak_const(self, prg, bound):
        prg.ground([('weak', [Number(bound)])])
        prg.assign_external(Function('bound', [Number(bound)]), True)

    def main(self, prg, files):
        #self.__theory.configure('propagate', 'full,1')
        self.__theory.register(prg)
        with ast.ProgramBuilder(prg) as bld:
            ast.parse_files(files, lambda stm: self.__theory.rewrite_ast(stm, bld.add))
        time_out_for_window, time_out_for_weak = self.get_TimeOut()
        i, ret = 0, None
        start_time = ''
        lastbound = 0
        interrupted_calls = 0
        non_interrupted_calls = 0
        makespan_time_window = []
        while i <= NUM_OF_TIME_WINDOWS:
            time_used = 0
            time_used1 = 0
            prg.configuration.solve.models = 0
            prg.cleanup()
            parts = self.step_to_ground(prg, i)
            prg.ground(parts)
            self.__theory.prepare(prg)
            bound = 0
            def on_model(model):
                nonlocal bound, start_time
                self.__theory.on_model(model)
                #if i != 0:
                a = self.__theory.assignment(model.thread_id)
                start_time, bound = self.get_total_facts(a, i)
            # ************************ DL Optimization ************************
            while True:
                prg.assign_external(Function('bound', [Number(lastbound-1)]), False)
                lastbound = bound
                tic = time.time()
                if time_used >= time_out_for_window:
                    interrupted_calls += 1
                    break
                with prg.solve(on_model=on_model, on_statistics=self.__on_statistics, async_=True, yield_=True) as handle:
                    handle.resume()
                    wait = handle.wait(time_out_for_window - time_used)
                    if not wait:
                        interrupted_calls += 1
                        break
                    model = handle.model()
                    if model is None:
                        non_interrupted_calls += 1
                        break
                toc = time.time()
                time_used += (toc - tic)
                self.add_new_constraint(prg, bound)
            
            # ************************ Setup Optimization [Weak constraint] ************************
            time_used = 0
            bound = lastbound
            self.weak_const(prg, lastbound)
            with prg.solve(on_model=on_model, on_statistics=self.__on_statistics, async_=True, yield_=True) as hnd:
                while True:
                    tic = time.time()
                    if time_used >= time_out_for_weak:
                        break
                    hnd.resume()
                    wait = hnd.wait(time_out_for_weak - time_used)
                    if not wait:
                        break
                    m = hnd.model()
                    if m is None:
                        #print('Optimum')
                        break
                    toc = time.time()
                    time_used += (toc - tic)

            #    makespan_time_window.append(lastbound)
            i = i + 1      # Go to the next Time Window

        for x in range(NUM_OF_TIME_WINDOWS):
            print('Completion Time for Window {} : {} '.format(x+1, makespan_time_window[x]))
        print('Interr Calls : {} '.format(interrupted_calls))
        print('UnInterr Calls : {} '.format(non_interrupted_calls))
        print('Makespan : {} '.format(bound))

sys.exit(int(clingo.clingo_main(Application('test'), sys.argv[1:])))
