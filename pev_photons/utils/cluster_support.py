#!/usr/bin/env python

import os
from itertools import product

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

    def submit(self, script, test=None, static_args=None,
               iters=None, submit_file=None, prefix=None):
        """ Construct a dag file and submit to the cluster.

        Parameters
        ----------
        script : str
            The name of the script to execute.
        test : bool
            Denotes whether to run a test job on a non-submitter node.
        static_args : dict, optional
            argument name and value pairs which do not change for each job.
        iters : dict
            argument names and lists of values pairs
            which have one for each jobs submitted.
        submit_file: str
            the .submit file for the dag to use.
        prefix : str
            The directory where output files are stored.

        Returns
        -------
        ex : str
            a bash executable to pass to os.system()
        """
        
        if static_args is not None:
            args = ' '.join('--{} {}'.format(key, static_args[key])
                                             for key in static_args.keys())
            args = ' {} '.format(args)
        else:
            args = ' '
        dag_file = os.path.join(self.temp_dir, self.name+'.dag')
        with open(dag_file, 'w+') as dag:
            for i, indices in enumerate(product(*iters.values())):
                arg = args + ' '.join('--{} {}'.format(iters.keys()[j], val)
                                      for j, val in enumerate(indices))
                if test:
                    return ' '.join(['python', script, arg])
                else:
                    self.write(dag=dag, index=i, arg=script+arg,
                               submit_file=submit_file,
                               prefix=prefix) 
        return 'condor_submit_dag -f {}'.format(dag_file)
