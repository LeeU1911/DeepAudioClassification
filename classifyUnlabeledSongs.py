# -*- coding: utf-8 -*-

from config import newDataPath, newSpectrogramsPath, pixelPerSecond, newSlicesPath, newDatasetPath
from audioFilesTools import isMono
from datasetTools import getDatasetName
from imageFilesTools import getImageData
# Import Pillow:
from PIL import Image
import os.path
from subprocess import Popen, PIPE, STDOUT
import pickle


#Tweakable parameters
desiredSize = 128

#Define
currentPath = os.path.dirname(os.path.realpath(__file__)) 


def classifyUnlabels():
	# classify
	print "classify Unlabels..."

	# vote

def sliceUnlabels():
	print "Creating spectrograms..."
	createSpectrogramsFromAudio()
	print "Spectrograms created!"

	print "Creating slices..."
	createSlicesFromSpectrograms(desiredSize)
	print "Slices created!"


#Creates .png whole spectrograms from mp3 files
def createSpectrogramsFromAudio():
	genresID = dict()
	files = os.listdir(newDataPath)
	files = [file for file in files if file.endswith(".mp3")]
	nbFiles = len(files)

	#Create path if not existing
	if not os.path.exists(os.path.dirname(newSpectrogramsPath)):
		try:
			os.makedirs(os.path.dirname(newSpectrogramsPath))
		except OSError as exc: # Guard against race condition
			if exc.errno != errno.EEXIST:
				raise

	#Rename files according to genre
	for index,filename in enumerate(files):
		print "Creating spectrogram for file {}/{}...".format(index+1,nbFiles)
		createSpectrogram(filename,filename)

#Create spectrogram from mp3 files
def createSpectrogram(filename,newFilename):
	#Create temporary mono track if needed
	if isMono(newDataPath+filename):
		command = "cp '{}' '/tmp/{}.mp3'".format(newDataPath+filename,newFilename)
	else:
		command = "sox '{}' '/tmp/{}.mp3' remix 1,2".format(newDataPath+filename,newFilename)
	p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True, cwd=currentPath)
	output, errors = p.communicate()
	if errors:
		print errors

	#Create spectrogram
	filename.replace(".mp3","")
	command = "sox '/tmp/{}.mp3' -n spectrogram -Y 200 -X {} -m -r -o '{}.png'".format(newFilename,pixelPerSecond,newSpectrogramsPath+newFilename)
	p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True, cwd=currentPath)
	output, errors = p.communicate()
	if errors:
		print errors

	#Remove tmp mono track
	if isMono(newDataPath+filename):
		os.remove("/tmp/{}.mp3".format(newFilename))



#Slices all spectrograms
def createSlicesFromSpectrograms(desiredSize):
	for filename in os.listdir(newSpectrogramsPath):
		if filename.endswith(".png"):
			sliceSpectrogram(filename,desiredSize)

#Creates slices from spectrogram
#TODO Improvement - Make sure we don't miss the end of the song
def sliceSpectrogram(filename, desiredSize):
	# genre = filename.split("_")[0] 	#Ex. Dubstep_19.png

	# Load the full spectrogram
	img = Image.open(newSpectrogramsPath+filename)

	#Compute approximate number of 128x128 samples
	width, height = img.size
	nbSamples = int(width/desiredSize)
	width - desiredSize

	#Create path if not existing
	filename = filename.replace(".mp3.png","")
	slicePath = newSlicesPath+"{}/".format(filename);
	if not os.path.exists(os.path.dirname(slicePath)):
		try:
			os.makedirs(os.path.dirname(slicePath))
		except OSError as exc: # Guard against race condition
			if exc.errno != errno.EEXIST:
				raise

	#For each sample
	for i in range(nbSamples):
		print "Creating slice: ", (i+1), "/", nbSamples, "for", filename
		#Extract and save 128x128 sample
		startPixel = i*desiredSize
		imgTmp = img.crop((startPixel, 1, startPixel + desiredSize, desiredSize + 1))
		imgTmp.save(newSlicesPath+"{}/{}_{}.png".format(filename,filename[:-4],i))

#Creates or loads dataset if it exists
def getUnlabeledDataset(unlabeledFileNames, sliceSize):
    print("[+] Dataset name: {}".format(getDatasetName(unlabeledFileNames,sliceSize)))
    if not os.path.isfile(newDatasetPath+"unlabeled_data.p"):
        print("[+] Creating dataset with {} slices of size {} per genre... ⌛️".format(unlabeledFileNames,sliceSize))
        createDatasetFromSlices(unlabeledFileNames, sliceSize) 
    else:
        print("[+] Using existing dataset")
    
    return loadDataset()

#Creates and save dataset from slices
def createDatasetFromSlices(unlabeledFileNames, sliceSize):
    data = []
    # find files in folder
    print("-> Adding {}...".format(unlabeledFileNames))
    
    #Get slices in unlabeledFileNames subfolder
    for filename in unlabeledFileNames:
	    filenames = os.listdir(newSlicesPath+filename)
	    filenames = [pngFileName for pngFileName in filenames if pngFileName.endswith('.png')]
	    # get image data and append to data
	    for pngFileName in filenames:
	        imgData = getImageData(newSlicesPath+filename+"/"+pngFileName, sliceSize)
	        data.append(imgData)
    print("    Dataset created! ✅")
    #Save
    saveDataset(data)

    return data

#Saves dataset
def saveDataset(data):
     #Create path for dataset if not existing
    if not os.path.exists(os.path.dirname(newDatasetPath)):
        try:
            os.makedirs(os.path.dirname(newDatasetPath))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    #SaveDataset
    print("[+] Saving dataset... ")
    pickle.dump(data, open("{}unlabeled_data.p".format(newDatasetPath), "wb" ))
    print("    Dataset saved! ✅💾")

#Loads dataset
#Mode = "train" or "test"
def loadDataset():
    #Load existing
    print("[+] Loading unlabeled dataset... ")
    data = pickle.load(open("{}unlabeled_data.p".format(newDatasetPath), "rb" ))
    print("    Unlabeled dataset loaded! ✅")
    return data