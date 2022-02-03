import tccontroller


JOBDIR = "/home/adurden/jobs/testing/"
JOB_TEMPLATE = "/home/adurden/tccontroller/templates/template.job"
TDCI_TEMPLATE = "/home/adurden/tccontroller/templates/tdci.in"
SCHEDULER = False


#tccontroller.sanity_test()

tc = tccontroller.tccontroller(JOBDIR, JOB_TEMPLATE, TDCI_TEMPLATE, SCHEDULER)

print("initialized tccontroller\n")

initial_xyzfile = "/home/adurden/jobs/testing/ethylene.xyz"

grad, recn, imcn = tc.nextstep(initial_xyzfile)

for i in range(0, 10):
  print("step done!")
  # do nuclear dynamics stuff here and gimmie a new xyzfile
  # The orbital and wfn data is just scraped from the previous tdci job directory
  # for this example we'll just use the same input file :D
  grad, recn, imcn = tc.nextstep(initial_xyzfile)
  print((grad,recn,imcn))

print("all done!")
