import os
import csv
from pathlib import Path
import argparse

class SamplingData:
    """A simple class containing the data for an individual sampling run."""
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Members
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Algorithm Info
    algorithmName = "--"
    author = "--"
    twise = -1.0
    # Rank
    rank = -1.0
    score = -1.0    
    # Model Infos
    modelName = "--"
    modelFeatures = "--"
    modelConstraints = "--"
    featureCombinations = -1.0
    timeout = -1.0
    # Averages + Intermediate Scores
    avgSize = -1.0
    avgSizeScore = -1.0
    avgRuntime = -1.0
    avgRuntimeScore = -1.0
    avgCoverage = -1.0
    avgCoverageScore = -1.0
    avgMemory = -1.0
    avgMemoryScore = -1.0
    avgROIC = -1.0
    avgMSOC = -1.0
    avgFIMD = -1.0
    avgICST = -1.0
    avgSimilarityScore = -1.0
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Header for csv export
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    csvHeader = ["Algorithm", "Author", "Feature Interaction", "Rank", "Score", "Package", "Avg. Features", "Avg. Constraints", "Feature Combinations", "Timeout", "Avg. Size", "Size Score", "Avg. Runtime", "Runtime Score", "Avg. Coverage", "Coverage Sore", "Avg. Memory", "Memory Score", "Avg. RoIC", "Avg. MSOC", "Avg. FIMD", "Avg.  ICST", "Similarity Score"]

    def getCSVData(self):
        allElements = []
        allElements.append(str(self.algorithmName))
        allElements.append(str(self.author))
        allElements.append(str(self.twise))
        allElements.append(str(self.rank))
        allElements.append(str(self.score))
        allElements.append(str(self.modelName))
        allElements.append(str(self.modelFeatures))
        allElements.append(str(self.modelConstraints))
        allElements.append(str(self.featureCombinations))
        allElements.append(str(self.timeout))
        allElements.append(str(self.avgSize))
        allElements.append(str(self.avgSizeScore))
        allElements.append(str(self.avgRuntime))
        allElements.append(str(self.avgRuntimeScore))
        allElements.append(str(self.avgCoverage))
        allElements.append(str(self.avgCoverageScore))
        allElements.append(str(self.avgMemory))
        allElements.append(str(self.avgMemoryScore))
        allElements.append(str(self.avgROIC))
        allElements.append(str(self.avgMSOC))
        allElements.append(str(self.avgFIMD))
        allElements.append(str(self.avgICST))
        allElements.append(str(self.avgSimilarityScore))
        return allElements

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 
#
# Global methods
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def getValidPathForInputRun(inputPath):
    """Validates the path required for the input run"""
    # Check if data path is valid
    if os.path.isfile(inputPath) and ".csv" in inputPath:
        #Direct file
        return inputPath
    return None

def createDataFromRun(inputFile):
    """Creates a new sampling data packet from a given input"""
    inputPath = getValidPathForInputRun(inputFile)
    if inputPath is None:
        print("Input path is invalid. Reference an output folder or a specific run .csv file.")
        return None

    sampleDataTable = {} # Contains Key: Algorithm Identifier, Value: Sample Data
    listOfParticipants = []
    with open(inputPath, "r") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=';')
        all_Lines = list(reader)

        # Extract list of all participants
        for line in all_Lines:
            algorithmIdentifier = line['Author'] + line['AlgorithmID']
            if not listOfParticipants.__contains__(algorithmIdentifier):
                listOfParticipants.append(algorithmIdentifier)

        # Parse results for each participant
        for author in listOfParticipants:
            # Create lists for averages
            sampleSizeTable = []
            sampleTimeTable = []
            sampleCoverageTable = []
            sampleMemoryTable = []
            sampleROICTable = []
            sampleMSOCTable = []
            sampleFIMDTable = []
            sampleICSTTable = []
            featureCombTable = []

            data = None
            # Process all lines
            for line in all_Lines:
                if author == (line['Author'] + line['AlgorithmID']):
                    # First line create 
                    if data is None:
                        # Create new dataset
                        data = SamplingData()
                        data.author = line['Author']
                        data.algorithmName = line['AlgorithmID']
                        data.twise = line['T-Value']
                        data.modelName = line['ModelName']
                        data.modelFeatures = line['Model_Features']
                        data.modelConstraints = line['Model_Constraints']
                        data.timeout = line['Timeout']
                    # Add data to compute averages
                    sampleSizeTable.append(float(line['Size']))
                    sampleTimeTable.append(float(line['Time']))
                    sampleCoverageTable.append(float(line['Coverage']))
                    sampleMemoryTable.append(float(line['TotalCreatedBytes']))
                    sampleROICTable.append(float(line['ROIC']))
                    sampleMSOCTable.append(float(line['MSOC']))
                    sampleFIMDTable.append(float(line['FIMD']))
                    sampleICSTTable.append(float(line['ICST']))
                    featureCombTable.append(float(line['Valid Conditions']))

            # Compute averages and save into map
            data.avgSize = getAverage(sampleSizeTable)
            data.avgRuntime = getAverage(sampleTimeTable)
            data.avgCoverage = getAverage(sampleCoverageTable)
            data.avgMemory = getAverage(sampleMemoryTable)
            data.avgROIC = getAverage(sampleROICTable)
            data.avgMSOC = getAverage(sampleMSOCTable)
            data.avgFIMD = getAverage(sampleFIMDTable)
            data.avgICST = getAverage(sampleICSTTable)
            data.featureCombinations = getAverage(featureCombTable)
            sampleDataTable[author] = data
    return list(sampleDataTable.values())

def getAverage(listOfFloats):
    sum = 0
    num = 0
    for fValue in listOfFloats:
        if fValue != -1:
            sum += float(fValue)
            num += 1
    if num == 0:
        return 0
    else:
        return float(sum) / float(num)

def checkOutputPath(outputPath):
    """Ensures that the output csv file exists and creates the file if necessary"""
    # Check if argument is file
    if not os.path.isfile(outputPath):
        # Create file with headers 
        with open(outputPath, "w") as csvfile:
            filewriter = csv.writer(csvfile, delimiter=";", quotechar="|", quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(SamplingData.csvHeader)

def saveData(outputPath, samplingData):
    """Saves the given sampling data to csv"""
    checkOutputPath(outputPath)

    # Get all datas and overwrite informations
    samplingDataListOrig = getData(outputPath)
    samplingDataList = []
    
    # Replace already present data
    for oldData in samplingDataListOrig:
        isReplaced = False
        for newData in samplingData:
            if (oldData.author + oldData.algorithmName) == (newData.author + newData.algorithmName):
                # replace entry
                samplingDataList.append(newData)
                isReplaced = True
                break
        if not isReplaced:
            samplingDataList.append(oldData)

    # Add new data
    for newData in samplingData:
        if not samplingDataList.__contains__(newData):
            samplingDataList.append(newData)
    
    # Save all data
    saveDataList(outputPath, samplingDataList)

def saveDataList(outputPath, samplingDataList):
    """Saves the given sampling data to csv"""
    checkOutputPath(outputPath)

    # Remove old file
    if os.path.isfile(outputPath):
        os.remove(outputPath)

    # Write all information with new information 
    with open(outputPath, "w", newline='') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=";", quotechar="|", quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow(SamplingData.csvHeader)
        for data in samplingDataList:
            filewriter.writerow(data.getCSVData())

def getData(outputPath):
    """Read the csv data by the given path and """
    checkOutputPath(outputPath)
    
    # read list of sampling data 
    samplingDataList = []
    with open(outputPath, "r") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=';')
        for line in reader:
            x = SamplingData()
            x.algorithmName = line[SamplingData.csvHeader[0]]
            x.author = line[SamplingData.csvHeader[1]]
            x.twise = float(line[SamplingData.csvHeader[2]])
            x.rank = float(line[SamplingData.csvHeader[3]])
            x.score = float(line[SamplingData.csvHeader[4]])
            x.modelName = line[SamplingData.csvHeader[5]]
            x.modelFeatures = float(line[SamplingData.csvHeader[6]])
            x.modelConstraints = float(line[SamplingData.csvHeader[7]])
            x.featureCombinations = float(line[SamplingData.csvHeader[8]])
            x.timeout = int(line[SamplingData.csvHeader[9]])
            x.avgSize = float(line[SamplingData.csvHeader[10]])
            x.avgSizeScore = float(line[SamplingData.csvHeader[11]])
            x.avgRuntime = float(line[SamplingData.csvHeader[12]])
            x.avgRuntimeScore = float(line[SamplingData.csvHeader[13]])
            x.avgCoverage = float(line[SamplingData.csvHeader[14]])
            x.avgCoverageScore = float(line[SamplingData.csvHeader[15]])
            x.avgMemory = float(line[SamplingData.csvHeader[16]])
            x.avgMemoryScore = float(line[SamplingData.csvHeader[17]])
            x.avgROIC = float(line[SamplingData.csvHeader[18]])
            x.avgMSOC = float(line[SamplingData.csvHeader[19]])
            x.avgFIMD = float(line[SamplingData.csvHeader[20]])
            x.avgICST = float(line[SamplingData.csvHeader[21]])
            x.avgSimilarityScore = float(line[SamplingData.csvHeader[22]])
            samplingDataList.append(x)
    return samplingDataList
    
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 
# Metrics = (Simple) (lowest best)
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def calculate_Simple(dataList, gSize, gRuntime, gCoverage, gSimilarity):
    # Size Subscore
    dataList.sort(key=lambda data: data.avgSize)
    rank = 1
    lastValue = -1
    for data in dataList:
        if lastValue == -1:
            data.avgSizeScore = rank
        elif lastValue == data.avgSize:
            # Same value => same rank
            data.avgSizeScore = rank
        else:
            # New Rank 
            rank += 1
            data.avgSizeScore = rank
        lastValue = data.avgSize
        
    # Runtime Subscore
    dataList.sort(key=lambda data: data.avgRuntime)
    rank = 1
    lastValue = -1
    for data in dataList:
        if lastValue == -1:
            data.avgRuntimeScore = rank
        elif lastValue == data.avgRuntime:
            # Same value => same rank
            data.avgRuntimeScore = rank
        else:
            # New Rank 
            rank += 1
            data.avgRuntimeScore = rank
        lastValue = data.avgRuntime

        
    # Coverage Subscore
    dataList.sort(key=lambda data: -data.avgCoverage)
    rank = 1
    lastValue = -1
    for data in dataList:
        if lastValue == -1:
            data.avgCoverageScore = rank
        elif lastValue == data.avgCoverage:
            # Same value => same rank
            data.avgCoverageScore = rank
        else:
            # New Rank 
            rank += 1
            data.avgCoverageScore = rank
        lastValue = data.avgCoverage

    # Runtime Similarity Subscore (FIMD)
    dataList.sort(key=lambda data: -data.avgFIMD)
    rank = 1
    lastValue = -1
    for data in dataList:
        if lastValue == -1:
            data.avgSimilarityScore = rank
        elif lastValue == data.avgFIMD:
            # Same value => same rank
            data.avgSimilarityScore = rank
        else:
            # New Rank 
            rank += 1
            data.avgSimilarityScore = rank
        lastValue = data.avgFIMD

    # Calculate score
    for data in dataList:
        data.score = (gSize * data.avgSizeScore) + (gRuntime * data.avgRuntimeScore) + (gCoverage * data.avgCoverageScore) + (gSimilarity * data.avgSimilarityScore)

    # Determine Rank
    dataList.sort(key=lambda data:data.score)
    for data in dataList:
        data.rank = 1 + dataList.index(data)

    return dataList
    
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 
# Metrics = (WeightRanked) (lowest best)
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def calculate_WeightRanked(dataList, gSize, gRuntime, gCoverage, gSimilarity):
    # Size Subscore
    dataList.sort(key=lambda data: data.avgSize)
    minimum = dataList[0].avgSize
    for data in dataList:
        data.avgSizeScore = data.avgSize / minimum
        
    # Runtime Subscore
    dataList.sort(key=lambda data: data.avgRuntime)
    minimum = dataList[0].avgRuntime
    for data in dataList:
        data.avgRuntimeScore = data.avgRuntime / minimum

    # Coverage Subscore
    dataList.sort(key=lambda data: -data.avgCoverage)
    minimum = dataList[0].avgCoverage
    for data in dataList:
        data.avgCoverageScore = data.avgCoverage / minimum

    # Runtime Similarity Subscore (FIMD)
    dataList.sort(key=lambda data: -data.avgFIMD)
    minimum = dataList[0].avgFIMD
    for data in dataList:
        data.avgFIMDScore = data.avgFIMD / minimum

    # Calculate score
    for data in dataList:
        data.score = (gSize * data.avgSizeScore) + (gRuntime * data.avgRuntimeScore) + (gCoverage * data.avgCoverageScore) + (gSimilarity * data.avgSimilarityScore)

    # Determine Rank (lowest best)
    dataList.sort(key=lambda data:data.score)
    for data in dataList:
        data.rank = 1 + dataList.index(data)

    return dataList
    
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 
# Metrics = (ReverseRanked) (highest best)
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def calculate_ReverseRanked(dataList, gSize, gRuntime, gCoverage, gSimilarity):
    # Size Subscore
    dataList.sort(key=lambda data: -data.avgSize)
    maximum = dataList[0].avgSize
    for data in dataList:
        data.avgSizeScore = maximum / data.avgSize
        
    # Runtime Subscore
    dataList.sort(key=lambda data: -data.avgRuntime)
    maximum = dataList[0].avgRuntime
    for data in dataList:
        data.avgRuntimeScore = maximum / data.avgRuntime

    # Coverage Subscore
    dataList.sort(key=lambda data: data.avgCoverage)
    maximum = dataList[0].avgCoverage
    for data in dataList:
        data.avgCoverageScore = maximum / data.avgCoverage

    # Runtime Similarity Subscore (FIMD)
    dataList.sort(key=lambda data: data.avgFIMD)
    maximum = dataList[0].avgFIMD
    for data in dataList:
        data.avgFIMDScore = maximum / data.avgFIMD

    # Calculate score
    for data in dataList:
        data.score = (gSize * data.avgSizeScore) + (gRuntime * data.avgRuntimeScore) + (gCoverage * data.avgCoverageScore) + (gSimilarity * data.avgSimilarityScore)

    # Determine Rank (Highest best)
    dataList.sort(key=lambda data: -data.score)
    for data in dataList:
        data.rank = 1 + dataList.index(data)

    return dataList
    
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 
# Metrics = (Individual) (lowest best)
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def calculate_Individual(dataList, gSize, gRuntime, gCoverage, gSimilarity):
    # Size Subscore
    for data in dataList:
        data.avgSizeScore = data.avgSize / data.featureCombinations
        
    # Runtime Subscore
    for data in dataList:
        data.avgRuntimeScore = data.avgRuntime / data.timeout
        
    # Coverage Subscore
    for data in dataList:
        data.avgCoverageScore = data.avgCoverage

    # Runtime Similarity Subscore (FIMD)
    for data in dataList:
        data.avgSimilarityScore = data.avgFIMD

    # Calculate score
    for data in dataList:
        data.score = (gSize * data.avgSizeScore) + (gRuntime * data.avgRuntimeScore) + (gCoverage * data.avgCoverageScore) + (gSimilarity * data.avgSimilarityScore)

    # Determine Rank (lowest best)
    dataList.sort(key=lambda data:data.score)
    for data in dataList:
        data.rank = 1 + dataList.index(data)

    return dataList