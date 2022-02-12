#!/usr/bin/python2.7

from __future__ import print_function
import numpy as np
import struct, shutil, os, subprocess, time





def tcstring_to_xyz(atoms,geom,filename):
  f = open(filename,'w')
  f.write(str(len(atoms))+"\n\n")
  for i in range(0,len(atoms)):
    f.write(str(atoms[i])+"   "+str(geom[3*i+0])+"    "+str(geom[3*i+1])+"    "+str(geom[3*i+2])+"\n")
  f.close()

def xyz_to_tcstring(filename):
  f = open(filename,'r')
  f.readline();f.readline()
  l = f.readline()
  atoms = []
  geom = []
  print(l.split(" "))
  while len(l.split(" "))==4:
    atoms.append(l.split(" ")[0])
    geom.append(l.split(" ")[1]) 
    geom.append(l.split(" ")[2]) 
    geom.append(l.split(" ")[3])
    l = f.readline()
  


def dict_to_file(d, filepath):
  f = open(filepath, 'w')
  for key, value in d.iteritems():
    f.write(str(key)+" "+str(value)+"\n")
  f.close()

def dicts_to_file(dlist, filepath):
  f = open(filepath, 'w')
  for d in dlist:
    for key, value in d.iteritems():
      f.write(str(key)+" "+str(value)+"\n")
  f.close()

# we may need to be careful about endian-ness if this runs on a different machine than TC
# this doesnt work. think we need ctypes for this
def read_bin_array(filepath):
  f = open(filepath, 'rb')
  return struct.unpack('d', f.read())

def read_csv_array(filepath):
  f = open(filepath, 'r')
  text = f.read()
  text = text.strip(", \n")
  return np.array(list(map(float, (text).split(","))))

def sanity_test():
  ref = [0.1111, 0.2222, 0.3333, 1.1111, 1.2222, 1.3333, 2.1111, 2.2222, 2.3333]
  test = read_bin_array("testarray.bin")
  if test == ref:
    print("sanity test passed")
    print("reference:\n"+str(ref)+"\n\ntest:\n"+str(test))
  else:
    print("sanity test failed :(\n")
    print("reference:\n"+str(ref)+"\n\ntest:\n"+str(test))

#sanity_test()


def search_replace_file(filepath, search, replace):
  p = subprocess.Popen('sed -i -e "s+'+search+'+'+replace+'+g" '+str(filepath), shell=True)
  p.wait()
  return 0


def makedirs(dirstr):
  for i in range(2, dirstr.count("/")+1):
    if not os.path.exists("/".join(dirstr.split("/")[0:i])):
      os.mkdir("/".join(dirstr.split("/")[0:i]))
  return os.path.exists(dirstr)


class job:
  def __init__(self, n, xyzpath, pjob, JOBDIR, JOB_TEMPLATE, TDCI_TEMPLATE, SCHEDULER=False):
    self.n = n
    self.pjob = pjob
    self.dir = JOBDIR+"electronic/"+str(n)+"/"
    self.JOBDIR=JOBDIR
    self.JOB_TEMPLATE=JOB_TEMPLATE
    self.TDCI_TEMPLATE=TDCI_TEMPLATE
    self.SCHEDULER=SCHEDULER
    self.xyzpath = xyzpath

  def start(self):
    p = subprocess.Popen( 'bash '+self.dir+'tdci.job', shell=True)
    return p


  def make_files(self):
    makedirs(self.dir)
    shutil.copy(self.xyzpath, self.dir+self.xyzpath.split("/")[-1]) # copy xyzfile
    shutil.copy(self.JOB_TEMPLATE, self.dir+"/tdci.job")
    time.sleep(2) # make sure file gets copied
    search_replace_file(self.dir+"tdci.job", "temppath", self.dir)
    search_replace_file(self.dir+"tdci.job", "tempname", "test"+str(self.n))
    tempname = "test"+str(self.n)+".in"
    shutil.copy(self.TDCI_TEMPLATE, self.dir+"/"+tempname)
    search_replace_file(self.dir+tempname, "coords.xyz", self.xyzpath.split("/")[-1]) 
    if self.n==0:
      search_replace_file(self.dir+tempname, "tdci_diabatize_orbs yes", "tdci_diabatize_orbs no")
      search_replace_file(self.dir+tempname, "tdci_recn_readfile recn_init.bin", "")
      search_replace_file(self.dir+tempname, "tdci_imcn_readfile imcn_init.bin", "")
      search_replace_file(self.dir+tempname, "tdci_prevorbs_readfile PrevC.bin", "")
      search_replace_file(self.dir+tempname, "tdci_prevcoords_readfile PrevCoors.bin", "")

    else: # Copy Prev Orbitals and Coords (in double4) for orbital diabatization
      pjobd = self.pjob.dir
      shutil.copy(pjobd+"/NewCoors.bin", self.dir+"/PrevCoors.bin")
      shutil.copy(pjobd+"/NewC.bin", self.dir+"/PrevC.bin")
      shutil.copy(pjobd+"/ReCn_end.bin", self.dir+"/recn_init.bin")
      shutil.copy(pjobd+"/ImCn_end.bin", self.dir+"/imcn_init.bin")

  def clean_files(self):
    if os.path.exists(self.dir):
      shutil.rmtree(self.dir)

  def run_interactive(self):
    # Run the job
    retries = 0
    while (retries < 20):
      self.clean_files()
      self.make_files()
      p = self.start()
      print("Started "+str(self.dir)+"\n")
      finished = 0
      # Periodically check if the process is finished
      while not finished:
        time.sleep(5)
        if self.check_status(p):
          finished = True
      # Make sure output is good
      outputgood = True
      grad, recn, imcn = None, None, None
      if not os.path.exists(self.dir+"tdcigrad.csv"):
        outputgood = False
        print("ERROR: tdcigrad.csv missing\n")
      if not os.path.exists(self.dir+"ReCn_end.csv"):
        outputgood = False
        print("ERROR: ReCn_end.csv missing\n")
      if not os.path.exists(self.dir+"ImCn_end.csv"):
        outputgood = False
        print("ERROR: ImCn_end.csv missing\n")
      if outputgood: # files exist, lets get the output
        grad = read_csv_array(self.dir+"tdcigrad.csv")
        recn = read_csv_array(self.dir+"ReCn_end.csv")
        imcn = read_csv_array(self.dir+"ImCn_end.csv")
        norm = np.sum(recn**2) + np.sum(imcn**2)
        print("Output looks good! Final wfn norm: "+str(norm))
        if ((norm<0.5) or (norm>2.0) or (np.isnan(norm))):
          print("ERROR: Norm out of bounds\n")
          outputgood = False
        if (np.sum(grad)<0.0001):
          print("WARNING: gradient is zero ("+str(np.sum(grad))+")\n")
        if (np.isnan(np.sum(grad))):
          print("ERROR: nan in gradient\n")
          outputgood = False
      
      if outputgood: # Everything checks out!
        return (grad, recn, imcn)
      else: # Outputs bad, try redoing the job!
        print("Output is bad. Restarting the job.")
      retries+=1
    print("Went through 20 retries and output is still bad T_T\n")
    return 1

      
  def check_status(self, p):
    if self.SCHEDULER:
      # TODO: Need to call squeue and decipher it's output
      pass
    else: 
      result = p.poll()
      print(result)
      if result != None: # returns None if still running
        print("Done!\n")
        return True
      else:
        print("Still running...\n")
        return False

  def output(self):
    grad = read_csv_array(self.dir+"tdcigrad.csv")
    recn = read_csv_array(self.dir+"ReCn_end.csv")
    imcn = read_csv_array(self.dir+"ImCn_end.csv")
    return (grad, recn, imcn)


class tccontroller:
  def __init__(self, JOBDIR, JOB_TEMPLATE, TDCI_TEMPLATE, SCHEDULER=False):
    self.N = 0
    self.jobs = []
    self.JOBDIR=JOBDIR
    self.JOB_TEMPLATE=JOB_TEMPLATE
    self.TDCI_TEMPLATE=TDCI_TEMPLATE
    self.SCHEDULER=SCHEDULER

  def nextstep(self, xyzpath):
    if self.N == 0:
      j = job(self.N, xyzpath, None, self.JOBDIR, self.JOB_TEMPLATE, self.TDCI_TEMPLATE, self.SCHEDULER)
    else:
      j = job(self.N, xyzpath, self.jobs[-1], self.JOBDIR, self.JOB_TEMPLATE, self.TDCI_TEMPLATE, self.SCHEDULER)
    self.jobs.append(j)
    self.N+=1
    j.run_interactive()
    return j.output()
    

    

    




