import tccontroller
import numpy as np



TERACHEM = "/home/adurden/terachem/build/bin/" # terachem executable stored here
# make sure you include temppath and tempname in your job template!
#  those keywords are search and replaced
job_template_contents = "#!/bin/bash\n\
                         source /home/adurden/.bashrc\n\
                         cd temppath\n\
                        "+TERACHEM+"terachem tempname.in > tempname.out\n"

JOB_TEMPLATE = "/home/adurden/tccontroller/templates/template.job"
f = open(JOB_TEMPLATE,'w')
f.write(job_template_contents)
f.close()


nfields = 1                # number of distinct fields (generally for multichromatic floquet)
nstep = 12000               # number of timesteps
tdci_simulation_time = 12   # in femtoseconds
tdci_options = {
  "gpus"                 : "1 0",
  "timings"              : "yes",
  "precision"            : "double",
  "threall"              : "1.0e-20",
  "convthre"             : "1.0e-6",
  "basis"                : "sto-3g",
  "coordinates"          : "coords.xyz", # <-- don't change this
  "method"               : "hf",
  "run"                  : "tdci", # <-- don't change this
  "charge"               : "0",
  "spinmult"             : "1",
  "csf_basis"            : "no",
  "tdci_simulation_time" : str(tdci_simulation_time),
  "tdci_nstep"           : str(nstep),
  "tdci_eshift"          : "gs",
  "tdci_stepprint"       : "1",
  "tdci_nfields"         : str(nfields),
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
  "tdci_fieldfile0"      : "field0.csv",

  # These options will be removed on first step, don't change them.
  "tdci_diabatize_orbs"  : "yes",
  "tdci_recn_readfile"   : "recn_init.bin",
  "tdci_imcn_readfile"   : "imcn_init.bin",
  "tdci_prevorbs_readfile": "PrevC.bin",
  "tdci_prevcoords_readfile": "PrevCoors.bin"
}

TDCI_TEMPLATE = "/home/adurden/tccontroller/templates/tdci.in"
tccontroller.dict_to_file(tdci_options, TDCI_TEMPLATE)

# Define the external field
# ======================================
# Field file should include values for half-steps, so the length of the array
#   should be 2*nsteps!

# Depending on the external field you want, you might have to write some
#   code here to generate the waveform, below is a CW tuned to ethylene
#   Function should accept np.arrays in units of AU time and return AU E-field units.
def f0_values(t):
  EPSILON_C = 0.00265316
  E_FIELD_AU = 5.142206707E+11
  HZtoAU = 2.418884E-17
  E_strength_Wm2 = 1.0E+16 # In W/m^2
  E_str = (np.sqrt(2.0*E_strength_Wm2 / EPSILON_C) )/E_FIELD_AU  # transform to au field units
  field_freq_hz = 3.444030610581e+15 # tuned to S0 <-> S1 for rabi flop example
  return E_str*np.sin(2.0*np.pi * field_freq_hz*HZtoAU * t)

FIELD_INFO = { "tdci_simulation_time": tdci_simulation_time,
               "nstep"               : nstep,
               "nfields"             : nfields,
               "f0"                  : f0_values
             }



# End field definition
# ======================================

JOBDIR = "/home/adurden/jobs/testing/"
SCHEDULER = False # Not implemented, but this will hook into sbatch/squeue

tc = tccontroller.tccontroller(JOBDIR, JOB_TEMPLATE, TDCI_TEMPLATE, FIELD_INFO, SCHEDULER)
print("initialized tccontroller\n")



# Doing the next TDCI step is as simple as calling tc.nextstep and feeding it the newest coordinates
initial_xyzfile = "/home/adurden/jobs/testing/ethylene.xyz"
grad, recn, imcn = tc.nextstep(initial_xyzfile)
print((grad,recn,imcn))

# Let's do 10 steps, just feeding TDCI the same geometry. 
for i in range(0, 10):
  print("step done!")
  grad, recn, imcn = tc.nextstep(initial_xyzfile)
  print((grad,recn,imcn))

print("all done!")
