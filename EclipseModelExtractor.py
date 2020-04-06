###
### Reads all eclipse projects in the working directory and extracts the model.xml file. To work the project should contain a model.xml in the root folder:
###
### TestProject
### ----model.xml
###
### The resulting model.xml is renamed after it's containing project. The resulting model would be named: TestProject.xml with the example above.
###

import os
import shutil
import glob

for file in glob.glob("." + os.path.sep +"**" + os.path.sep + "model.xml", recursive=True):
    fromPath = file
    toPath = file.replace(os.path.sep + "model", "")
    print("Extracted model: " + file.replace("." + os.path.sep, "").replace(os.path.sep + "model", ""))
    shutil.move(fromPath, toPath)
