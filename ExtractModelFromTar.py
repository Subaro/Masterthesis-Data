###
### Reads all tar.gz files in the working directory and extracts the model.xml file. To work the tar.gz should have the folowing form:
###
### testFile.tar.gz
### ----2008-01-02_19-55-04
### --------model.xml
###
### The resulting model.xml is renamed after it's containing folder. The resulting model would be named: 2008-01-02_19-55-04.xml with the example above.
###

import os
import sys
import tempfile
import tarfile
import shutil
import glob
import numpy as np 

def py_files(members):
    for tarinfo in members:
        if os.path.splitext(tarinfo.name)[1] == ".xml":
            yield tarinfo

def extractModel(tarFile):
    tarName = tarFile
    targetModelName = os.path.splitext(os.path.splitext(tarName)[0])[0]
    print(targetModelName)
    my_tar = tarfile.open(tarName)
    my_tar.extract(targetModelName + "/model.xml", "./")
    print("Extracted model: " + targetModelName + ".xml")
    fromPath = os.path.join(os.path.join(os.getcwd(), targetModelName), "model.xml")
    toPath = os.path.join(os.getcwd(), targetModelName + ".xml")
    shutil.move(fromPath, toPath)
    shutil.rmtree(os.path.join(os.getcwd(), targetModelName))

for file in glob.glob("*.tar.gz"):
    extractModel(file)
