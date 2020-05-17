import os
import samplingData
import argparse
import glob

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 
# Main
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Prepares the argument parser. The following arguments are accepted by the evaluator:
parser = argparse.ArgumentParser(prog="reqEval",description='Process arguments...')
parser.add_argument('--mode', 
                    type=str,
                    choices=["simple", "weighranked", "inverseranked", "individual", all], 
                    dest="mode", 
                    help='current mode to calculate score')
parser.add_argument('--in', 
                    type=str, 
                    dest="input", 
                    help='path to a data run')
parser.add_argument('-out', 
                    type=str, 
                    dest="output", 
                    help='path to output table')
parser.add_argument('--runtime', 
                    type=int, 
                    dest="sampletime", 
                    help='emphasis for the sample runtime criteria. Default: 1')
parser.add_argument('--size', 
                    type=int, 
                    dest="samplesize", 
                    help='emphasis for the sample size criteria. Default: 1')
parser.add_argument('--coverage', 
                    type=int, dest="samplecoverage", 
                    help='emphasis for the sample coverage criteria. Default: 1')
parser.add_argument('--similarity', 
                    type=int, dest="samplesimilarity", 
                    help='emphasis for the sample similarity criteria. Default: 1')
args = parser.parse_args() 
sampleTime = 1
sampleSize = 1
sampleCoverage = 1
sampleSimilarity = 1
if args.sampletime:
    sampleTime = args.sampletime
if args.samplesize:
    sampleSize = args.samplesize
if args.samplecoverage:
    sampleCoverage = args.samplecoverage
if args.samplesimilarity:
    sampleCoverage = args.samplesimilarity
print("Starting evaluator with following priorities: (Size: " + str(sampleSize) + ", Time: " + str(sampleTime) + ", Coverage: " + str(sampleCoverage) + ", Similarity: " + str(sampleSimilarity) + ")...")

def saveData(output, data, mode, printPrios):
    path = args.output[:-4]
    if printPrios:
        samplingData.saveDataList(path + "_general_(" + sampleSize + "," + sampleTime + "," + sampleCoverage + "," + sampleSimilarity + ")" + ".csv", data)
    else:
        samplingData.saveDataList(path + "_general" + ".csv", data)
    
# Read input and create sampling data from given input run (overrides old run)
if args.input is not None:
    if os.path.isdir(args.input):
        # Read all files and process the "input*.csv files"
        listOfData = []
        for path in glob.glob(args.input + "\\*.csv"):
            for data in samplingData.createDataFromRun(path):
                listOfData.append(data)
        saveData(args.output, listOfData, "general", False)
    else:
        inputData = samplingData.createDataFromRun(args.input)
        saveData(args.output, inputData, "general", False)

if args.output is not None and args.mode is not None:
    # It is a file => Get all entries and calculate the scores
    path = args.output[:-4]
    participantsDataList = samplingData.getData(path + "_general" + ".csv")

    # Calculate score
    if args.mode == "simple":
        participantsDataList = samplingData.calculate_Simple(participantsDataList, sampleSize, sampleTime, sampleCoverage, sampleSimilarity)
        saveData(args.output, participantsDataList, args.mode, True)
    elif args.mode == "weighranked": 
        participantsDataList = samplingData.calculate_WeightRanked(participantsDataList, sampleSize, sampleTime, sampleCoverage, sampleSimilarity)
        saveData(args.output, participantsDataList, args.mode, True)
    elif args.mode == "inverseranked":
        participantsDataList = samplingData.calculate_ReverseRanked(participantsDataList, sampleSize, sampleTime, sampleCoverage, sampleSimilarity)
        saveData(args.output, participantsDataList, args.mode, True)
    elif args.mode == "individual":
        participantsDataList = samplingData.calculate_Individual(participantsDataList, sampleSize, sampleTime, sampleCoverage, sampleSimilarity)
        saveData(args.output, participantsDataList, args.mode, True)
    elif args.mode == "all":
        # simple
        participantsDataList = samplingData.calculate_Simple(participantsDataList, sampleSize, sampleTime, sampleCoverage, sampleSimilarity)
        saveData(args.output, participantsDataList, args.mode, True)
        # weightranked
        participantsDataList = samplingData.calculate_WeightRanked(participantsDataList, sampleSize, sampleTime, sampleCoverage, sampleSimilarity)
        saveData(args.output, participantsDataList, args.mode, True)
        # inverseranked
        participantsDataList = samplingData.calculate_ReverseRanked(participantsDataList, sampleSize, sampleTime, sampleCoverage, sampleSimilarity)
        saveData(args.output, participantsDataList, args.mode, True)
        # individual
        participantsDataList = samplingData.calculate_Individual(participantsDataList, sampleSize, sampleTime, sampleCoverage, sampleSimilarity)
        saveData(args.output, participantsDataList, args.mode, True)
