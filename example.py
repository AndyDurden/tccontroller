import tccontroller



TERACHEM = "/home/adurden/terachem/build/bin/" # terachem executable stored here
job_template_contents = "#!/bin/bash\n\
                         source /home/adurden/.bashrc\n\
                         cd temppath\n\
                        "+TERACHEM+"terachem tempname.in > tempname.out\n"

JOB_TEMPLATE = "/home/adurden/tccontroller/templates/template.job"
f = open(JOB_TEMPLATE,'w')
f.write(job_template_contents)
f.close()


nstep = 2000
tdci_options = {
  "gpus"                 : "1 0",
  "timings"              : "yes",
  "precision"            : "double",
  "threall"              : "1.0e-20",
  "convthre"             : "1.0e-6",
  "basis"                : "6-31gs",
  "coordinates"          : "coords.xyz", # <-- don't change this
  "method"               : "hf",
  "run"                  : "tdci", # <-- don't change this
  "charge"               : "0",
  "spinmult"             : "1",
  "csf_basis"            : "no",
  "tdci_simulation_time" : "2",
  "tdci_nstep"           : str(nstep),
  "tdci_eshift"          : "gs",
  "tdci_stepprint"       : "1",
  "tdci_nfields"         : "1",
  "tdci_laser_freq"      : "2.5311296E+15",  
  "tdci_photoneng"       : "0.38467766",
  "tdci_fstrength"       : "1.0E+16",   # TODO: replace field generation params with file readin
  "tdci_fdirection"      : "x",
  "tdci_ftype"           : "cw",
  "tdci_corrfn_t"        : "p0",
  "tdci_write_field"     : "no",
  "tdci_floquet"         : "no",
  "tdci_floquet_photons" : "3",
  "casci"                : "yes",
  "ci_solver"            : "direct",
  "dcimaxiter"           : "300",
  "dciprintinfo"         : "yes",
  "dcipreconditioner"    : "orbenergy",
  "closed"               : "7",
  "active"               : "2",
  "cassinglets"          : "3",
  "castriplets"          : "0",
  "cascharges"           : "yes",
  "cas_ntos"             : "yes",
  "tdci_gradient"        : "yes",  # <-- don't change this

  # These options will be removed on first step, don't change them.
  "tdci_diabatize_orbs"  : "yes",
  "tdci_recn_readfile"   : "recn_init.bin",
  "tdci_imcn_readfile"   : "imcn_init.bin",
  "tdci_prevorbs_readfile": "PrevC.bin",
  "tdci_prevcoords_readfile": "PrevCoors.bin"
}

TDCI_TEMPLATE = "/home/adurden/tccontroller/templates/tdci.in"
tccontroller.dict_to_file(tdci_options, TDCI_TEMPLATE)

JOBDIR = "/home/adurden/jobs/testing/"
SCHEDULER = False # Not implemented, but this will hook into sbatch/squeue

tc = tccontroller.tccontroller(JOBDIR, JOB_TEMPLATE, TDCI_TEMPLATE, SCHEDULER)
print("initialized tccontroller\n")



# Doing the next TDCI step is as simple as calling tc.nextstep and feeding it the newest coordinates
initial_xyzfile = "/home/adurden/jobs/testing/ethylene.xyz"
grad, recn, imcn = tc.nextstep(initial_xyzfile)


# Let's do 10 steps, just feeding TDCI the same geometry. 
for i in range(0, 10):
  print("step done!")
  grad, recn, imcn = tc.nextstep(initial_xyzfile)
  print((grad,recn,imcn))

print("all done!")
