#!/usr/bin/env python
import os
import zipfile
import sys

def zipdir(path, ziph):
    # ziph is zipfile handle
    filenames = ['astarnavigator.py', 'mynavigatorhelpers.py', 'mycreatepathnetwork.py']
    count = len(filenames)

    for root, dirs, files in os.walk(path):
        for file in files:
            if file in filenames:
                ziph.write(os.path.join(root, file))
                count -= 1
	return count

if __name__ == '__main__':
    gtusername = raw_input("Please enter your GT username (such as mriedl3): ")
    zipfilename = gtusername + "_hw4.zip"
    zipf = zipfile.ZipFile(zipfilename, 'w', zipfile.ZIP_DEFLATED)
    num_files = zipdir('.', zipf)
    zipf.close()
    if num_files != 0:
		os.remove(zipfilename)
		sys.exit("Please run the script from the correct directory containing all the files needed for the submission!") 
    else:
        print "Successfully created", zipfilename, "in the homework4 folder."
