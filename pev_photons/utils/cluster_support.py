#!/usr/bin/env python

import os

class DagMaker():
    """ Class for executing DagMan related tasks

    Attributes
    ----------
    name : str
        Name of the dag
    temp_dir : float
        where to store dag and log files (typically scratch space)
    """
    def __init__(self, name=None, temp_dir=None):
        self.name = name
        self.temp_dir = temp_dir

    def remove_old(self, prefix=None):
        """ Remove dag related files from previous submission.

        Parameters
        ----------
        prefix : str
            The directory where output files are stored.
        """
        print('Deleting '+self.name+' files...')
        os.system('rm '+os.path.join(self.temp_dir, self.name)+'*')
        os.system('rm '+os.path.join(prefix, 'dagman', self.name)+'*')

    def write(self, dag, index=None, arg=None,
              submit_file=None, prefix=None):
        """ Write a job into a dag file.

        Parameters
        ----------
        dag : str
            A .dag file.
        index : int
            The job number.
        arg : str
            The arguments for the executable.
        submit_file : str
            The .submit file for the dag.
        prefix : str
            The directory where output files are stored.
        """
        dag.write('JOB {} {}\n'.format(index, submit_file))
        dag.write('VARS {} ARGS=\"{}\"\n'.format(index,arg))
        dag.write('VARS {} log_dir=\"{}/logs/{}\"\n'.format(index, self.temp_dir,
                                                            self.name))
        dag.write('VARS {} out_dir=\"{}/dagman/{}\"\n'.format(index, prefix,
                                                              self.name))
