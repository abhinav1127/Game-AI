#!/usr/bin/env python
import os
import zipfile
import sys


gtusername = raw_input("Please enter your GT username (such as mriedl3):\n")
zipfilename = gtusername + "_hw5.zip"

print "\nNote: If you have .py files (mycreatepathnetwork, astarnavigator) in your homework5 folder, upon running the tests  the .pyc files would be overwritten. So if you want to use the instructor's solutions, then please keep only the instructor's .pyc files (and not the .py files) in the homework5 folder."

while True:
	createpath_pyc_flag = raw_input("\nPlease enter 'y' if you want to include your mycreatepathnetwork.py file in the submission else 'n' to include the mycreatepathnetwork.pyc file: \n")
	if createpath_pyc_flag == "y":
		createpath_use_pyc = 0
		print "The script will add the student's mycreatepathnetwork.py file to the submission"
		break
	elif createpath_pyc_flag == "n":
		createpath_use_pyc = 1
		print "The script will add the mycreatepathnetwork.pyc file to the submission"
		break
	else:
		print "Please enter either 'y' or 'n'"
		

while True:
	astar_pyc_flag = raw_input("\nPlease enter 'y' if you want to include your astarnavigator.py file in the submission else 'n' to include astarnavigator.pyc file: \n")
	if astar_pyc_flag == "y":
		astar_use_pyc = 0
		print "The script will add the student's astarnavigator.py file to the submission"
		break
	elif astar_pyc_flag == "n":
		astar_use_pyc = 1
		print "The script will add the astarnavigator.pyc file to the submission"
		break
	else:
		print "Please enter either 'y' or 'n'"

        
def zipdir(path, ziph):
	# ziph is zipfile handle
	filenames = ['MyMinion.py', 'mynavigatorhelpers.py']
	createpathfiles = ['mycreatepathnetwork.py', 'mycreatepathnetwork.pyc']
	astarfiles = ['astarnavigator.py', 'astarnavigator.pyc']

	if createpath_use_pyc == 1:
		filenames.append(createpathfiles[1])
	elif createpath_use_pyc == 0:
		filenames.append(createpathfiles[0])

	if astar_use_pyc == 1:
		filenames.append(astarfiles[1])
	elif astar_use_pyc == 0:
		filenames.append(astarfiles[0])

	tot_files = len(filenames)
	count = 0
	for root, dirs, files in os.walk(path):
		for file in files:
		    if file in filenames:
		        ziph.write(os.path.join(root, file))
		        count += 1

	return tot_files, count


zipf = zipfile.ZipFile(zipfilename, 'w', zipfile.ZIP_DEFLATED)

req_num_files, num_files = zipdir('.', zipf)

zipf.close()

if req_num_files != num_files:
	os.remove(zipfilename)
	sys.exit("\nSubmission script was not able to find all the necessary .py or .pyc files needed for the submission!") 
elif num_files == 0:
	os.remove(zipfilename)
	sys.exit("\nPlease run the script from the correct directory containing all the files needed for the submission!") 
else:
    print "\nSuccessfully created", zipfilename, "in the homework5 folder."
    

