
import os
import sys
import yaml

import plasTeX.client

def createLpilBaseTexFile(texFilePath) :

  # ensure the file extension IS '.tex'
  if not texFilePath.endswith('.tex') : texFilePath += '.tex'
  texFilePath = texFilePath.replace('..', '.')

  # read the beginning of the file looking for TeX-Magic comments
  preAmble  = None
  postAmble = None
  with open(texFilePath) as tf :
    while True :
      aLine = tf.readline()
      if not aLine : break
      aLine = aLine.strip()
      if not aLine.startswith('%') :
        if len(aLine) : break
        else : continue
      if not aLine.find('=') : continue
      lineFields = aLine.split('=')
      aKey = lineFields[0].lower()
      if len(lineFields) < 2 : continue
      aValue = lineFields[1].strip()
      if -1 < aKey.find('!lpil') :
        if -1 < aKey.find('preamble') :
          preAmble = aValue
        if -1 < aKey.find('postamble') :
          postAmble = aValue

  # if no pre or post ambles found... just use this given file path
  if not preAmble or not postAmble : return texFilePath

  # Fabricate a LPiL specific '.tex' file which inputs the pre/post
  # ambles.
  newTexFilePath = texFilePath.replace('.tex', '_lpil.tex')
  with open(newTexFilePath, 'w') as tf :
    tf.write(f"\input{{{preAmble}}}\n")
    tf.write(f"\input{{{texFilePath}}}\n")
    tf.write(f"\input{{{postAmble}}}\n")
  return newTexFilePath

def fabricatePlasTexArguments(buildDir) :

  # if there are no arguments... fabricate the '-h' help switch...
  if len(sys.argv) < 2 : return ["-h"]

  # manipulate the command line arguments adding ours in the correct
  # places...
  pArgv = []
  lArgv =  [
    f"--dir={buildDir}",
    #"--plugins",
    #"gerbyPlasTeX",
    #"lpilPlasTeX",
    #"--"
  ]
  fArgv = []
  nextIsConfig = False
  nextIsRenderer = False
  verbose = False
  for anArg in sys.argv[1:] :
    if anArg == '--verbose' or anArg == '-v' :
      verbose = True
      continue
    if anArg == '--config' or anArg == '-c' :
      nextIsConfig = True
      continue
    if nextIsConfig :
      nextIsConfig = False
      pArgv.extend(['--config', anArg])
      continue
    if anArg == '--help' or anArg == '-h' :
      pArgv.append(anArg)
      continue
    if nextIsRenderer :
      nextIsRenderer = False
      pArgv.extend(['--renderer', anArg])
      continue
    if anArg.startswith('--renderer') :
      nextIsRenderer = True
      continue
    pArgv.append(anArg)
  print(yaml.dump(pArgv))
  print(yaml.dump(lArgv))
  print(yaml.dump(fArgv))
  filePath = pArgv.pop()
  if filePath.startswith('-') :
    pArgv.append(filePath)
    filePath = None
  theArgs = pArgv + lArgv + fArgv
  if filePath :
    theArgs.append(filePath)
  if verbose :
    print("-------------------")
    print(yaml.dump(theArgs))
    print("-------------------")
  return theArgs

def cli() :

  # make sure the build/web directory exists...
  buildDir = os.path.join('build', 'web')
  os.makedirs(buildDir, exist_ok=True)

  # manipulate the command line arguments...
  theArgs = fabricatePlasTexArguments(buildDir)

  # check the file for TeX-MagicComments...
  theFile = theArgs[len(theArgs)-1]
  if not theFile.startswith('-') :
    lpilFile = createLpilBaseTexFile(theFile)
    theArgs[len(theArgs)-1] = lpilFile
    print(f"Running PlasTeX on: {lpilFile}")

  # Now do the work (hand off to plasTeX)...
  try :
    plasTeX.client.main(theArgs)
  except KeyboardInterrupt :
    pass
