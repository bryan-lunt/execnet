"""
Some parts of HTCondor gateway for execnet

(c) 2016 Bryan Lunt 
"""

import os
import tempfile

submit_and_ssh_script = """#!/bin/bash

sub_output=$(condor_submit -terse << EOF
executable=/bin/sleep
transfer_executable=false
arguments=180
universe=vanilla
queue 1
EOF
)

#should add some error detection here.

jobid=$(echo $sub_output | sed 's/ .*//g')

#now ssh to that job and apply all further options to the SSH process.
condor_ssh_to_job -auto-retry -remove-on-interrupt ${jobid} -- $*
"""

def write_htcondor_submitssh_script(destination=None):
	scriptfile = tempfile.NamedTemporaryFile(delete=False)
	scriptfile.write(submit_and_ssh_script)
	scriptfile.flush()
	import stat as _stat
	os.chmod(scriptfile.name,_stat.S_IXUSR|_stat.S_IWUSR|_stat.S_IRUSR)
	return scriptfile.name

from gateway_io import popen_bootstrapline

def htcondor_args(spec):
    # NOTE: If changing this, you need to sync those changes to vagrant_args
    # as well, or, take some time to further refactor the commonalities of
    # ssh_args and vagrant_args.
    #TODO: create the submit_and_ssh script in a temporary file so that this is self-contained.
    remotepython = spec.python or "python"
    #args = ["./submit_and_ssh"]
    from gateway_htcondor import write_htcondor_submitssh_script
    args = [ write_htcondor_submitssh_script() ]
    #if spec.ssh_config is not None:
    #    args.extend(['-F', str(spec.ssh_config)])
    #
    #args.extend(spec.ssh.split())
    remotecmd = '%s -c "%s"' % (remotepython, popen_bootstrapline)
    args.append(remotecmd)
    return args
