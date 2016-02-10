'''
Created on Feb 12, 2014

@author: adh
'''
import logging
import os

from certfuzz.file_handlers.basicfile import BasicFile
from certfuzz.fuzztools.ppid_observer import check_ppid
from certfuzz.iteration.iteration_base3 import IterationBase3
from certfuzz.tc_pipeline.tc_pipeline_linux import LinuxTestCasePipeline
from certfuzz.helpers.misc import fixup_path
from certfuzz.testcase.testcase_linux import LinuxTestcase


logger = logging.getLogger(__name__)


class LinuxIteration(IterationBase3):
    tcpipeline_cls = LinuxTestCasePipeline

    def __init__(self,
                 seedfile=None,
                 seednum=None,
                 workdirbase=None,
                 outdir=None,
                 sf_set=None,
                 uniq_func=None,
                 config=None,
                 fuzzer_cls=None,
                 runner_cls=None,
                 ):

        IterationBase3.__init__(self,
                                seedfile=seedfile,
                                seednum=seednum,
                                workdirbase=workdirbase,
                                outdir=outdir,
                                sf_set=sf_set,
                                uniq_func=uniq_func,
                                config=config,
                                fuzzer_cls=fuzzer_cls,
                                runner_cls=runner_cls,
                                )

        self.quiet_flag = self._iteration_counter < 2

        self.testcase_base_dir = os.path.join(self.outdir, 'crashers')

        self.pipeline_options = {'use_valgrind': self.cfg['analyzer']['use_valgrind'],
                                 'use_pin_calltrace': self.cfg['analyzer']['use_pin_calltrace'],
                                 'minimize_crashers': self.cfg['runoptions']['minimize'],
                                 'minimize_to_string': self.cfg['runoptions']['minimize_to_string'],
                                 'uniq_log': os.path.join(self.cfg['directories']['results_dir'], 'uniquelog.txt'),
                                 'local_dir': fixup_path(self.cfg['directories']['working_dir']),
                                 'minimizertimeout': self.cfg['runoptions']['minimizer_timeout'],
                                 'minimizable': self.fuzzer_cls.is_minimizable and self.cfg['runoptions']['minimize'],
                                 }

    def __enter__(self):
        IterationBase3.__enter__(self)
        check_ppid()
        return self.go

    def _pre_fuzz(self):
        self._fuzz_opts = self.cfg['fuzzer']
        IterationBase3._pre_fuzz(self)

    def _pre_run(self):
        self._runner_options = self.cfg['runner']

        if self.quiet_flag:
            self._runner_options['hideoutput'] = True
        self._runner_cmd_template = self.cfg['target']['cmdline_template']

        IterationBase3._pre_run(self)

    def _construct_testcase(self):
        with LinuxTestcase(cfg=self.cfg,
                      seedfile=self.seedfile,
                      fuzzedfile=BasicFile(self.fuzzer.output_file_path),
                      program=self.cfg['target']['program'],
                      debugger_timeout=self.cfg['debugger']['runtimeout'],
                      killprocname=self.cfg['target']['killprocname'],
                      backtrace_lines=self.cfg['debugger']['backtracelevels'],
                      crashers_dir=self.testcase_base_dir,
                      workdir_base=self.working_dir,
                      seednum=self.seednum,
                      range=self.r) as testcase:
            # put it on the list for the analysis pipeline
            self.testcases.append(testcase)
