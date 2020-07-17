# For parsing arguments
import argparse
import os
# For opening respective folders
import subprocess
import time
# For timestamping files
from datetime import datetime
from glob import glob
# For plotting
from pathlib import Path
from tkinter import *
# Tkinter + Plotting
from tkinter import filedialog
from tkinter.ttk import *
import json
import matplotlib.cm as cmx
import matplotlib as mpl
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# Helper
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def parseArguments():
    ''' Parses the arguments and returns the args object. '''
    # Prepare the argument parser. The following arguments are accepted by the evaluator:
    parser = argparse.ArgumentParser(
        prog="reqEval", description='Process arguments...')
    parser.add_argument('--in',
                        type=str,
                        dest="input",
                        help='path to a data run')
    parser.add_argument('--out',
                        type=str,
                        dest="output",
                        help='path to output table')
    parser.add_argument('--size',
                        type=int,
                        dest="samplesize",
                        help='emphasis for the sample size criteria. Default: 1')
    parser.add_argument('--runtime',
                        type=int,
                        dest="sampletime",
                        help='emphasis for the sample runtime criteria. Default: 1')
    parser.add_argument('--coverage',
                        type=int, dest="samplecoverage",
                        help='emphasis for the sample coverage criteria. Default: 1')
    parser.add_argument('--similarity',
                        type=int, dest="samplesimilarity",
                        help='emphasis for the sample similarity criteria. Default: 0')
    parser.add_argument('--memory',
                        type=int, dest="samplememory",
                        help='emphasis for the memory consumption. Default: 0')
    parser.add_argument('--gui', help='starts the gui mode',
                        action='store_true')
    parser.add_argument('--tiraInput',
                        type=str,
                        dest="tiraInput",
                        help='path to the tira input run')
    return parser.parse_args()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
#
#
#
#
#
#
#
#
# Prioritization
#
#
#
#
#
#
#
#
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def getPrioritization(arguments):
    # Get size
    size = 1
    if arguments.samplesize:
        size = arguments.samplesize
    # Get runtime
    time = 1
    if arguments.sampletime:
        time = arguments.sampletime
    # Get coverage
    coverage = 1
    if arguments.samplecoverage:
        coverage = arguments.samplecoverage
    # Get similarity
    similarity = 0
    if arguments.samplesimilarity:
        similarity = arguments.samplesimilarity
    # Get memory
    memory = 0
    if arguments.samplememory:
        memory = arguments.samplememory
    return Prioritization(size, time, coverage, similarity, memory)


class Prioritization:
    ''' A simple data class containing information of the prioritization of the user. '''
    size = 1.0
    time = 1.0
    coverage = 1.0
    memory = 0.0
    similarity = 0.0

    def __init__(self, size, time, coverage, similarity, memory):
        self.size = size
        self.time = time
        self.coverage = coverage
        self.similarity = similarity
        self.memory = memory

    def copy(self):
        return Prioritization(self.size, self.time, self.coverage, self.similarity, self.memory)

    def __str__(self):
        return "[S-" + str(self.size) + ",T-" + str(self.time) + ",C-" + str(self.coverage) + ",Sim-" + str(self.similarity) + ",M-" + str(self.memory) + "]"

    def printExlusively(self, exclusive):
        if exclusive == "size":
            return "[T-" + str(self.time) + ",C-" + str(self.coverage) + ",Sim-" + str(self.similarity) + ",M-" + str(self.memory) + "]"
        elif exclusive == "time":
            return "[S-" + str(self.size) + ",C-" + str(self.coverage) + ",Sim-" + str(self.similarity) + ",M-" + str(self.memory) + "]"
        elif exclusive == "coverage":
            return "[S-" + str(self.size) + ",T-" + str(self.time) + ",Sim-" + str(self.similarity) + ",M-" + str(self.memory) + "]"
        elif exclusive == "similarity":
            return "[S-" + str(self.size) + ",T-" + str(self.time) + ",C-" + str(self.coverage) + ",M-" + str(self.memory) + "]"
        elif exclusive == "memory":
            return "[S-" + str(self.size) + ",T-" + str(self.time) + ",C-" + str(self.coverage) + ",Sim-" + str(self.similarity) + "]"

    def identical(self, other):
        ''' Compares the given prioritization if they are identical. '''
        return self.size == other.size and self.time == other.time and self.coverage == other.coverage and self.memory == other.memory and self.similarity == other.similarity

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
#
#
#
#
#
#
#
#
# SamplingFrame
#
#
#
#
#
#
#
#
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class SamplingFrame:
    ''' Data class containing all data '''

    # Header for the average overview
    headerAveraged = [
        "Prioritization",
        "Algorithm",
        "NBS",
        "NBS Rank",
        "SRBS",
        "SRBS Rank",
        "WRBS",
        "WRBS Rank",
        "IWRBS",
        "IWRBS Rank",
        "Avg. Size",
        "Avg. Time",
        "Avg. Coverage",
        "Avg. Similarity",
        "Avg. Memory",
        "Avg. Normalized Size",
        "Avg. Normalized Time",
        "Avg. Normalized Memory",
        "NBS Subscore Size",
        "NBS Subscore Time",
        "NBS Subscore Coverage",
        "NBS Subscore Similarity",
        "NBS Subscore Memory",
        "SRBS Subscore Size",
        "SRBS Subscore Time",
        "SRBS Subscore Coverage",
        "SRBS Subscore Similarity",
        "SRBS Subscore Memory",
        "WRBS Subscore Size",
        "WRBS Subscore Time",
        "WRBS Subscore Coverage",
        "WRBS Subscore Similarity",
        "WRBS Subscore Memory",
        "IWRBS Subscore Size",
        "IWRBS Subscore Time",
        "IWRBS Subscore Coverage",
        "IWRBS Subscore Similarity",
        "IWRBS Subscore Memory"
    ]

    # Header for all entries
    header = [
        "Author",
        "Algorithm",
        "T-Wise",
        "System Name",
        "System Features",
        "System Constraints",
        "System Iteration",
        "System Interactions",
        "System Timeout",
        "System Memory Throughput",
        "Memory Created Bytes MB",
        "Sample Size",
        "Sample Time",
        "Sample Coverage",
        "Sample Similarity",
        "Sample Memory",
        "ROIC",
        "MSOC",
        "FIMD",
        "ICST",
        'Nom. Sample Size',
        'Nom. Sample Time',
        'Nom. Sample Memory'
    ]

    data = pd.DataFrame  # Contains
    average = pd.DataFrame  # Contains the averaged data and scores
    extension = ".csv"

    def __init__(self):
        self.data = pd.DataFrame(columns=self.header)
        self.average = pd.DataFrame(columns=self.headerAveraged)

    def getData(self):
        return self.data

    def getAverageData(self):
        return self.average

    def saveAverage(self, absoluteSavePath):
        ''' Computes the average overview and saves it accordingly. '''
        # Remove old file
        if os.path.isfile(absoluteSavePath + self.extension):
            os.remove(absoluteSavePath + self.extension)

        # Save new version
        self.average.to_csv(absoluteSavePath + self.extension, sep=";")

    def save(self, absoluteSavePath):
        ''' Saves all data as csv object. The given path should not contain any extension. '''
        # Remove old file
        if os.path.isfile(absoluteSavePath + self.extension):
            os.remove(absoluteSavePath + self.extension)

        # Save new version
        self.data.to_csv(absoluteSavePath + self.extension, sep=";")

    def computeScores(self, absoluteSavePath, prioritizationList):
        ''' Computes all subscores and scores and saves the results in the respective output folder. '''
        # Clean average object
        self.average = self.average.iloc[0:0]

        # Compute everything for all prioritizations
        for prio in prioritizationList:
            # Compute average version
            self.getBasicAverages(prio)

            # Compute score for each prioritization
            self.calculate_Individual(prio)
            self.calculate_Simple(prio)
            self.calculate_Weighted(prio)
            self.calculate_InverseWeighted(prio)

        # Save data
        self.saveAverage(absoluteSavePath + "_averaged")

    def getBasicAverages(self, prioritization):
        ''' Calculates the averaged values used for the score computations '''
        algorithmList = self.data['Algorithm'].unique()

        for algorithm in algorithmList:
            data = {}

            # Save Algorithm
            data['Algorithm'] = algorithm
            # Save Prio
            data['Prioritization'] = str(prioritization)

            algorithmData = self.data[(self.data['Algorithm'] == algorithm)]

            filteredData = algorithmData[(algorithmData['Sample Size'] >= 0)]
            data['Avg. Size'] = filteredData['Sample Size'].mean()

            filteredData = algorithmData[(algorithmData['Sample Time'] >= 0)]
            data['Avg. Time'] = filteredData['Sample Time'].mean()

            filteredData = algorithmData[(
                algorithmData['Sample Coverage'] >= 0)]
            data['Avg. Coverage'] = filteredData['Sample Coverage'].mean()

            filteredData = algorithmData[(
                algorithmData['Sample Similarity'] >= 0)]
            data['Avg. Similarity'] = filteredData['Sample Similarity'].mean()

            filteredData = algorithmData[(algorithmData['Sample Memory'] >= 0)]
            data['Avg. Memory'] = filteredData['Sample Memory'].mean()

            filteredData = algorithmData[(
                algorithmData['Nom. Sample Size'] >= 0)]
            data['Avg. Normalized Size'] = filteredData['Nom. Sample Size'].mean()

            filteredData = algorithmData[(
                algorithmData['Nom. Sample Time'] >= 0)]
            data['Avg. Normalized Time'] = filteredData['Nom. Sample Time'].mean()

            filteredData = algorithmData[(
                algorithmData['Nom. Sample Memory'] >= 0)]
            data['Avg. Normalized Memory'] = filteredData['Nom. Sample Memory'].mean()

            newEntry = pd.Series(data)
            self.average = self.average.append(newEntry, ignore_index=True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #
    # Data Handling (Saving, Loading, Importing)
    #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def load(self, absoluteInputPath):
        ''' Reads the sampling data from the all files in the given input path.  '''
        # 1. Empty current data
        self.data = self.data.iloc[0:0]

        if os.path.isdir(str(absoluteInputPath)):
            # Read all files and process the "input*.csv files"
            for path in glob(os.path.join(absoluteInputPath, "*.csv")):
                self.loadFromFile(path)
        elif os.path.isfile(str(absoluteInputPath)):
            self.loadFromFile(absoluteInputPath)

    def loadFromFile(self, absoluteFilePath):
        ''' Creates a new sampling data entry for the given file '''
        # Read file
        fileData = pd.read_csv(absoluteFilePath, sep=";")

        # Iterate all rows and mere into parent frame
        for _, row in fileData.iterrows():
            # Extract data
            data = {'Author': row['Author'],
                    'Algorithm': row['AlgorithmID'],
                    'T-Wise': row['T-Value'],
                    'System Name': row['ModelName'],
                    'System Features': row['Model_Features'],
                    'System Constraints': row['Model_Constraints'],
                    'System Iteration': row['SystemIteration'],
                    'System Interactions': row['Valid Conditions'],
                    'System Timeout': row['Timeout'],
                    'System Memory Throughput': row['Throughput'],
                    'Memory Created Bytes MB': row['TotalCreatedBytes'],
                    'Sample Size': row['Size'],
                    'Sample Time': row['Time'],
                    'Sample Coverage': row['Coverage'],
                    'Sample Similarity': row['FIMD'],
                    'Sample Memory': row['TotalCreatedBytes'],
                    'ROIC': row['ROIC'],
                    'MSOC': row['MSOC'],
                    'FIMD': row['FIMD'],
                    'ICST': row['ICST'],
                    'Nom. Sample Size': 1 - (row['Size'] / row['Valid Conditions']),
                    'Nom. Sample Time': 1 - (row['Time'] / row['Timeout']),
                    'Nom. Sample Memory': 1 - (row['TotalCreatedBytes'] / row['Valid Conditions']),
                    }
            if data['Nom. Sample Memory'] < 0:
                data['Nom. Sample Memory'] = 0
            self.data = self.data.append(pd.Series(data), ignore_index=True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #
    # Metrics = (Individual) (highest best) (in class)
    #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def calculate_Individual(self, prioritization):
        ''' Calculates the NBS score for all entries '''
        prioritizationFilter = self.average[self.average['Prioritization'] == str(
            prioritization)]
        for i, _ in prioritizationFilter.iterrows():
            # Size Subscore
            self.average.at[i, 'NBS Subscore Size'] = self.average.at[i,
                                                                      'Avg. Normalized Size']
            # Time Subscore
            self.average.at[i, 'NBS Subscore Time'] = self.average.at[i,
                                                                      'Avg. Normalized Time']
            # Coverage Subscore
            self.average.at[i, 'NBS Subscore Coverage'] = self.average.at[i,
                                                                          'Avg. Coverage']
            # Similarity Subscore (FIMD)
            self.average.at[i, 'NBS Subscore Similarity'] = self.average.at[i,
                                                                            'Avg. Similarity']
            # Memory Subscore
            self.average.at[i, 'NBS Subscore Memory'] = self.average.at[i,
                                                                        'Avg. Normalized Memory']
            # Calculate Score
            self.average.at[i, 'NBS'] = \
                (prioritization.size * self.average.at[i, 'NBS Subscore Size']) + \
                (prioritization.time * self.average.at[i, 'NBS Subscore Time']) + \
                (prioritization.coverage * self.average.at[i, 'NBS Subscore Coverage']) + \
                (prioritization.similarity * self.average.at[i, 'NBS Subscore Similarity']) + \
                (prioritization.similarity *
                 self.average.at[i, 'NBS Subscore Memory'])
        # Determine ranks
        prioritizationFilter = self.average[self.average['Prioritization'] == str(
            prioritization)]
        rank = 1
        lastValue = -1
        for i, _ in prioritizationFilter.sort_values(by='NBS', ascending=False).iterrows():
            if lastValue == -1:
                self.average.at[i, 'NBS Rank'] = rank
            elif lastValue == self.average.at[i, 'NBS']:
                # Same value => same rank
                self.average.at[i, 'NBS Rank'] = rank
            else:
                # New Rank
                rank += 1
                self.average.at[i, 'NBS Rank'] = rank
            lastValue = self.average.at[i, 'NBS']

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #
    # Metrics = (Simple) (lowest best)
    #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def calculate_Simple(self, prioritization):
        prioritizationFilter = self.average[self.average['Prioritization'] == str(
            prioritization)]
        # ---------------------------
        # Size Subscore
        rank = 1
        lastValue = -1

        for i, _ in prioritizationFilter.sort_values(by='Avg. Size', ascending=True).iterrows():
            if lastValue == -1:
                self.average.at[i, 'SRBS Subscore Size'] = rank
            elif lastValue == self.average.at[i, 'Avg. Size']:
                # Same value => same rank
                self.average.at[i, 'SRBS Subscore Size'] = rank
            else:
                # New Rank
                rank += 1
                self.average.at[i, 'SRBS Subscore Size'] = rank
            lastValue = self.average.at[i, 'Avg. Size']
        # ---------------------------
        # Time Subscore
        rank = 1
        lastValue = -1
        for i, _ in prioritizationFilter.sort_values(by='Avg. Time', ascending=True).iterrows():
            if lastValue == -1:
                self.average.at[i, 'SRBS Subscore Time'] = rank
            elif lastValue == self.average.at[i, 'Avg. Time']:
                # Same value => same rank
                self.average.at[i, 'SRBS Subscore Time'] = rank
            else:
                # New Rank
                rank += 1
                self.average.at[i, 'SRBS Subscore Time'] = rank
            lastValue = self.average.at[i, 'Avg. Time']
        # ---------------------------
        # Coverage Subscore
        rank = 1
        lastValue = -1
        for i, _ in prioritizationFilter.sort_values(by='Avg. Coverage', ascending=False).iterrows():
            if lastValue == -1:
                self.average.at[i, 'SRBS Subscore Coverage'] = rank
            elif lastValue == self.average.at[i, 'Avg. Coverage']:
                # Same value => same rank
                self.average.at[i, 'SRBS Subscore Coverage'] = rank
            else:
                # New Rank
                rank += 1
                self.average.at[i, 'SRBS Subscore Coverage'] = rank
            lastValue = self.average.at[i, 'Avg. Coverage']
        # ---------------------------
        # Similarity Subscore
        rank = 1
        lastValue = -1
        for i, _ in prioritizationFilter.sort_values(by='Avg. Similarity', ascending=False).iterrows():
            if lastValue == -1:
                self.average.at[i, 'SRBS Subscore Similarity'] = rank
            elif lastValue == self.average.at[i, 'Avg. Similarity']:
                # Same value => same rank
                self.average.at[i, 'SRBS Subscore Similarity'] = rank
            else:
                # New Rank
                rank += 1
                self.average.at[i, 'SRBS Subscore Similarity'] = rank
            lastValue = self.average.at[i, 'Avg. Similarity']
        # ---------------------------
        # Memory Subscore
        rank = 1
        lastValue = -1
        for i, _ in prioritizationFilter.sort_values(by='Avg. Memory', ascending=True).iterrows():
            if lastValue == -1:
                self.average.at[i, 'SRBS Subscore Memory'] = rank
            elif lastValue == self.average.at[i, 'Avg. Memory']:
                # Same value => same rank
                self.average.at[i, 'SRBS Subscore Memory'] = rank
            else:
                # New Rank
                rank += 1
                self.average.at[i, 'SRBS Subscore Memory'] = rank
            lastValue = self.average.at[i, 'Avg. Memory']
        # ---------------------------
        # Calculate score
        for i, _ in prioritizationFilter.iterrows():
            self.average.at[i, 'SRBS'] = \
                (prioritization.size * self.average.at[i, 'SRBS Subscore Size']) + \
                (prioritization.time * self.average.at[i, 'SRBS Subscore Time']) + \
                (prioritization.coverage * self.average.at[i, 'SRBS Subscore Coverage']) + \
                (prioritization.similarity * self.average.at[i, 'SRBS Subscore Similarity']) + \
                (prioritization.memory *
                 self.average.at[i, 'SRBS Subscore Memory'])
        # ---------------------------
        # Determine ranks
        prioritizationFilter = self.average[self.average['Prioritization'] == str(
            prioritization)]
        rank = 1
        lastValue = -1
        for i, _ in prioritizationFilter.sort_values(by='SRBS', ascending=True).iterrows():
            if lastValue == -1:
                self.average.at[i, 'SRBS Rank'] = rank
            elif lastValue == self.average.at[i, 'SRBS']:
                # Same value => same rank
                self.average.at[i, 'SRBS Rank'] = rank
            else:
                # New Rank
                rank += 1
                self.average.at[i, 'SRBS Rank'] = rank
            lastValue = self.average.at[i, 'SRBS']

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #
    # Metrics = (Weighted) (lowest best)
    #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def calculate_Weighted(self, prioritization):
        prioritizationFilter = self.average[self.average['Prioritization'] == str(
            prioritization)]
        # ---------------------------
        # Size Subscore
        if prioritization.size != 0:
            minimum = self.average['Avg. Size'].min()
            for i, _ in prioritizationFilter.iterrows():
                self.average.at[i, 'WRBS Subscore Size'] = self.average.at[i,
                                                                           'Avg. Size'] / minimum
        # ---------------------------
        # Time Subscore
        if prioritization.time != 0:
            minimum = self.average['Avg. Time'].min()
            for i, _ in prioritizationFilter.iterrows():
                self.average.at[i, 'WRBS Subscore Time'] = self.average.at[i,
                                                                           'Avg. Time'] / minimum
        # ---------------------------
        # Coverage Subscore
        if prioritization.coverage != 0:
            maximum = self.average['Avg. Coverage'].max()
            for i, _ in prioritizationFilter.iterrows():
                self.average.at[i, 'WRBS Subscore Coverage'] = maximum / self.average.at[i,
                                                                                         'Avg. Coverage']
        # ---------------------------
        # Similarity Subscore
        if prioritization.similarity != 0:
            maximum = self.average['Avg. Similarity'].max()
            for i, _ in prioritizationFilter.iterrows():
                self.average.at[i, 'WRBS Subscore Similarity'] = maximum / self.average.at[i,
                                                                                           'Avg. Similarity']
        # ---------------------------
        # Memory Subscore
        if prioritization.memory != 0:
            minimum = self.average['Avg. Memory'].min()
            for i, _ in prioritizationFilter.iterrows():
                self.average.at[i, 'WRBS Subscore Memory'] = self.average.at[i,
                                                                             'Avg. Memory'] / minimum
        # ---------------------------
        # Calculate score
        for i, _ in prioritizationFilter.iterrows():
            wrbs = 0
            if prioritization.size != 0:
                wrbs += prioritization.size * \
                    self.average.at[i, 'WRBS Subscore Size']
            if prioritization.time != 0:
                wrbs += prioritization.time * \
                    self.average.at[i, 'WRBS Subscore Time']
            if prioritization.coverage != 0:
                wrbs += prioritization.coverage * \
                    self.average.at[i, 'WRBS Subscore Coverage']
            if prioritization.similarity != 0:
                wrbs += prioritization.similarity * \
                    self.average.at[i, 'WRBS Subscore Similarity']
            if prioritization.memory != 0:
                wrbs += prioritization.memory * \
                    self.average.at[i, 'WRBS Subscore Memory']
            self.average.at[i, 'WRBS'] = wrbs

        # Determine ranks
        prioritizationFilter = self.average[self.average['Prioritization'] == str(
            prioritization)]
        rank = 1
        lastValue = -1
        for i, _ in prioritizationFilter.sort_values(by='WRBS', ascending=True).iterrows():
            if lastValue == -1:
                self.average.at[i, 'WRBS Rank'] = rank
            elif lastValue == self.average.at[i, 'WRBS']:
                # Same value => same rank
                self.average.at[i, 'WRBS Rank'] = rank
            else:
                # New Rank
                rank += 1
                self.average.at[i, 'WRBS Rank'] = rank
            lastValue = self.average.at[i, 'WRBS']

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #
    # Metrics = (Inverse Weigthed) (highest best)
    #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def calculate_InverseWeighted(self, prioritization):
        prioritizationFilter = self.average[self.average['Prioritization'] == str(
            prioritization)]
        # ---------------------------
        # Size Subscore
        if prioritization.size != 0:
            maximum = self.average['Avg. Size'].max()
            for i, _ in prioritizationFilter.iterrows():
                self.average.at[i, 'IWRBS Subscore Size'] = maximum / self.average.at[i,
                                                                                      'Avg. Size']
        # ---------------------------
        # Time Subscore
        if prioritization.time != 0:
            maximum = self.average['Avg. Time'].max()
            for i, _ in prioritizationFilter.iterrows():
                self.average.at[i, 'IWRBS Subscore Time'] = maximum / self.average.at[i,
                                                                                      'Avg. Time']
        # ---------------------------
        # Coverage Subscore
        if prioritization.coverage != 0:
            minimum = self.average['Avg. Coverage'].min()
            for i, _ in prioritizationFilter.iterrows():
                self.average.at[i, 'IWRBS Subscore Coverage'] = self.average.at[i,
                                                                                'Avg. Coverage'] / minimum
        # ---------------------------
        # Similarity Subscore
        if prioritization.similarity != 0:
            minimum = self.average['Avg. Similarity'].min()
            for i, _ in prioritizationFilter.iterrows():
                self.average.at[i, 'IWRBS Subscore Similarity'] = self.average.at[i,
                                                                                  'Avg. Similarity'] / minimum
        # ---------------------------
        # Memory Subscore
        if prioritization.memory != 0:
            maximum = self.average['Avg. Memory'].max()
            for i, _ in prioritizationFilter.iterrows():
                self.average.at[i, 'IWRBS Subscore Memory'] = maximum / self.average.at[i,
                                                                                        'Avg. Memory']
        # ---------------------------
        # Calculate score
        for i, _ in prioritizationFilter.iterrows():
            iwrbs = 0
            if prioritization.size != 0:
                iwrbs += prioritization.size * \
                    self.average.at[i, 'IWRBS Subscore Size']
            if prioritization.time != 0:
                iwrbs += prioritization.time * \
                    self.average.at[i, 'IWRBS Subscore Time']
            if prioritization.coverage != 0:
                iwrbs += prioritization.coverage * \
                    self.average.at[i, 'IWRBS Subscore Coverage']
            if prioritization.similarity != 0:
                iwrbs += prioritization.similarity * \
                    self.average.at[i, 'IWRBS Subscore Similarity']
            if prioritization.memory != 0:
                iwrbs += prioritization.memory * \
                    self.average.at[i, 'IWRBS Subscore Memory']
            self.average.at[i, 'IWRBS'] = iwrbs

        # Determine ranks
        prioritizationFilter = self.average[self.average['Prioritization'] == str(
            prioritization)]
        rank = 1
        lastValue = -1
        for i, _ in prioritizationFilter.sort_values(by='IWRBS', ascending=False).iterrows():
            if lastValue == -1:
                self.average.at[i, 'IWRBS Rank'] = rank
            elif lastValue == self.average.at[i, 'IWRBS']:
                # Same value => same rank
                self.average.at[i, 'IWRBS Rank'] = rank
            else:
                # New Rank
                rank += 1
                self.average.at[i, 'IWRBS Rank'] = rank
            lastValue = self.average.at[i, 'IWRBS']

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
#
#
#
#
#
#
#
#
# GUI
#
#
#
#
#
#
#
#
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class RequirementEvaluator:
    ''' The graphical class of our requirements evaluator. '''
    # plot markers
    markers = ("+", "+", "+", "+", "+", "+")
    # UI Variables
    master = None
    frame = Frame
    menubar = Menu
    labelDataStatusValue, labelDataEntriesValue, labelDataAlgorithmsValue = Label, Label, Label
    listEvalList = Listbox
    labelPlotName = Text
    plotFrame = Frame
    grayscaleMode, logarithmicMode, gridMode = IntVar, IntVar, IntVar
    varWidth, varHeight, varDPI, varLeft, varTop, varBottom, varRight, varXSpace, varYSpace = DoubleVar, DoubleVar, DoubleVar, DoubleVar, DoubleVar, DoubleVar, DoubleVar, DoubleVar, DoubleVar
    overrideWidthHeight, overrideLeftRight, overrideTopBottom, overrideSpace = IntVar, IntVar, IntVar, IntVar
    # Data Variables
    samplingFrame = SamplingFrame
    args = None
    samplePrioitization = Prioritization
    sizeSteps = DoubleVar
    sizeVar, timeVar, coverageVar, similarityVar, memoryVar = DoubleVar, DoubleVar, DoubleVar, DoubleVar, DoubleVar
    sizeVarEnd, timeVarEnd, coverageVarEnd, similarityVarEnd, memoryVarEnd = DoubleVar, DoubleVar, DoubleVar, DoubleVar, DoubleVar
    plotListEntries = []  # List containing the different prioritizations to plot

    def plot_addToList(self):
        ''' Adds the current priority to the plotting list it it is not already available.  '''
        copy = self.samplePrioitization.copy()

        # Check if the same is already available
        alreadyInList = False
        for prio in self.plotListEntries:
            alreadyInList = copy.identical(prio)

        if not alreadyInList:
            self.plotListEntries.append(copy)
            self.listEvalList.insert(END, copy)

    def plot_clearList(self):
        ''' Removes all entries of the plotting list. '''
        self.listEvalList.delete(0, END)
        self.plotListEntries.clear()

    def plot_calculateScoreForList(self):
        ''' Computes all scores for all prioritizations '''

    def plot_plotList(self):
        ''' Plots all lists. '''
        # Remove all old plots
        self.plot_removePlots()

        # Check if data is available
        if self.samplingFrame.data is None or len(self.samplingFrame.data) == 0:
            # Case: No data available inform user
            Label(self.plotFrame, text="No data loaded to plot!").pack()
        else:
            # Compute
            boxPlot = False
            if len(self.plotListEntries) == 0:
                self.samplingFrame.computeScores(
                    os.path.join(self.args.output, "scores"), [self.samplePrioitization])
                boxPlot = True
            elif len(self.plotListEntries) == 1:
                self.samplingFrame.computeScores(
                    os.path.join(self.args.output, "scores"), self.plotListEntries)
                boxPlot = True
            else:
                self.samplingFrame.computeScores(
                    os.path.join(self.args.output, "scores"), self.plotListEntries)

            jet = plt.get_cmap('Dark2')
            if self.isGrayscale():
                jet = plt.get_cmap('gray')

            cNorm = colors.Normalize(vmin=0, vmax=6)
            scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
            scalarMap.get_clim()

            # Boxplot when only one priority
            figure1 = None
            if boxPlot:
                # Create Boxplots
                if(self.overrideWidthHeight.get() == 1):
                    figure1 = plt.Figure(
                        figsize=(int(self.varWidth.get()), int(self.varHeight.get())), dpi=int(self.varDPI.get()))
                else:
                    self.varWidth.set(20)
                    self.varHeight.set(5)
                    self.varDPI.set(100)
                    figure1 = plt.Figure(figsize=(20, 5), dpi=100)
                self.plot_createBarPlot("NBS (highest-best)", figure1, 141, self.samplingFrame.getAverageData(
                ), 'Algorithm', 'Prioritization', 'NBS', scalarMap)
                self.plot_createBarPlot("SRBS (lowest-best)", figure1, 142, self.samplingFrame.getAverageData(
                ), 'Algorithm', 'Prioritization', 'SRBS', scalarMap)
                self.plot_createBarPlot("WRBS (lowest-best)", figure1, 143, self.samplingFrame.getAverageData(
                ), 'Algorithm', 'Prioritization', 'WRBS', scalarMap)
                self.plot_createBarPlot("IWRBS (highest-best)", figure1, 144, self.samplingFrame.getAverageData(
                ), 'Algorithm', 'Prioritization', 'IWRBS', scalarMap)

                bar = FigureCanvasTkAgg(figure1, self.plotFrame)
                bar.draw()
                bar.get_tk_widget().pack()
            else:
                # Create scatter
                if(self.overrideWidthHeight.get() == 1):
                    figure1 = plt.Figure(
                        figsize=(int(self.varWidth.get()), int(self.varHeight.get())), dpi=int(self.varDPI.get()))
                else:
                    self.varWidth.set(20)
                    self.varHeight.set(6)
                    self.varDPI.set(100)
                    figure1 = plt.Figure(figsize=(20, 6), dpi=100)
                self.plot_createPlot("NBS (highest-best)", figure1, 141, self.samplingFrame.getAverageData(
                ), 'Algorithm', 'Prioritization', 'NBS', scalarMap)
                self.plot_createPlot("SRBS (lowest-best)", figure1, 142, self.samplingFrame.getAverageData(
                ), 'Algorithm', 'Prioritization', 'SRBS', scalarMap)
                self.plot_createPlot("WRBS (lowest-best)", figure1, 143, self.samplingFrame.getAverageData(
                ), 'Algorithm', 'Prioritization', 'WRBS', scalarMap)
                self.plot_createPlot("IWRBS (highest-best)", figure1, 144, self.samplingFrame.getAverageData(
                ), 'Algorithm', 'Prioritization', 'IWRBS', scalarMap)

                figure1.autofmt_xdate(rotation=70)

                if(self.overrideLeftRight.get() == 1):
                    figure1.subplots_adjust(left=float(
                        self.varLeft.get()), right=float(self.varRight.get()))
                else:
                    self.varLeft.set(0.15)
                    self.varRight.set(0.99)
                    figure1.subplots_adjust(left=float(
                        self.varLeft.get()), right=float(self.varRight.get()))

                if(self.overrideTopBottom.get() == 1):
                    figure1.subplots_adjust(top=float(
                        self.varTop.get()), bottom=float(self.varBottom.get()))
                else:
                    self.varTop.set(0.9)
                    self.varBottom.set(0.25)
                    figure1.subplots_adjust(top=float(
                        self.varTop.get()), bottom=float(self.varBottom.get()))

                if(self.overrideSpace.get() == 1):
                    figure1.subplots_adjust(wspace=float(
                        self.varXSpace.get()), hspace=float(self.varYSpace.get()))
                else:
                    self.varXSpace.set(0.1)
                    self.varYSpace.set(0.1)
                    figure1.subplots_adjust(wspace=float(
                        self.varXSpace.get()), hspace=float(self.varYSpace.get()))

                # Show in UI
                scatter = FigureCanvasTkAgg(figure1, self.plotFrame)
                scatter.draw()
                scatter.get_tk_widget().pack()

            # Export
            if self.isExporting():
                figure1.savefig(self.plot_getPlotExportPath(".pdf"))

    def plot_plotComparison(self, title, xtitle, xaxis, ytitle, yaxis):
        ''' Plots all lists. '''
        # Remove all old plots
        self.plot_removePlots()

        # Check if data is available
        if self.samplingFrame.data is None or len(self.samplingFrame.data) == 0:
            # Case: No data available inform user
            Label(self.plotFrame, text="No data loaded to plot!").pack()
        else:
            jet = plt.get_cmap('Dark2')
            if self.isGrayscale():
                jet = plt.get_cmap('gray')

            cNorm = colors.Normalize(vmin=0, vmax=6)
            scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
            scalarMap.get_clim()

            # Create scatter
            figure1 = None
            if(self.overrideWidthHeight.get() == 1):
                figure1 = plt.Figure(
                    figsize=(int(self.varWidth.get()), int(self.varHeight.get())), dpi=int(self.varDPI.get()))
            else:
                self.varWidth.set(7)
                self.varHeight.set(6)
                self.varDPI.set(100)
                figure1 = plt.Figure(figsize=(7, 6), dpi=100)

            plot = self.plot_createComparePlot(title, figure1, 111, self.samplingFrame.getData(
            ), 'Algorithm', xaxis, yaxis, scalarMap)
            plot.set_xlabel(xtitle)
            if self.isLogarithmicMode():
                plot.set_ylabel(ytitle + ' in logarithmic scale')
            else:
                plot.set_ylabel(ytitle)

            figure1.autofmt_xdate(rotation=70)
            if(self.overrideLeftRight.get() == 1):
                figure1.subplots_adjust(left=float(
                    self.varLeft.get()), right=float(self.varRight.get()))
            else:
                self.varLeft.set(0.15)
                self.varRight.set(0.99)
                figure1.subplots_adjust(left=float(
                    self.varLeft.get()), right=float(self.varRight.get()))

            if(self.overrideTopBottom.get() == 1):
                figure1.subplots_adjust(top=float(
                    self.varTop.get()), bottom=float(self.varBottom.get()))
            else:
                self.varTop.set(0.9)
                self.varBottom.set(0.13)
                figure1.subplots_adjust(top=float(
                    self.varTop.get()), bottom=float(self.varBottom.get()))

            if(self.overrideSpace.get() == 1):
                figure1.subplots_adjust(wspace=float(
                    self.varXSpace.get()), hspace=float(self.varYSpace.get()))
            else:
                self.varXSpace.set(0.1)
                self.varYSpace.set(0.1)
                figure1.subplots_adjust(wspace=float(
                    self.varXSpace.get()), hspace=float(self.varYSpace.get()))

            # Export
            if self.isExporting():
                figure1.savefig(self.plot_getPlotExportPath(".pdf"))

            # Show in UI
            scatter = FigureCanvasTkAgg(figure1, self.plotFrame)
            scatter.draw()
            scatter.get_tk_widget().pack()

    def plot_plotRangeInternal(self, priorityList, variable):
        # Remove all old plots
        self.plot_removePlots()

        # Check if data is available
        if self.samplingFrame.getData() is None or len(self.samplingFrame.getData()) == 0:
            # Case: No data available inform user
            Label(self.plotFrame, text="No data loaded to plot!").pack()
            return

        # Compute
        boxPlot = False
        if len(priorityList) == 0:
            self.samplingFrame.computeScores(
                os.path.join(self.args.output, "scores"), [self.samplePrioitization])
            boxPlot = True
        elif len(priorityList) == 1:
            self.samplingFrame.computeScores(
                os.path.join(self.args.output, "scores"), priorityList)
            boxPlot = True
        else:
            self.samplingFrame.computeScores(
                os.path.join(self.args.output, "scores"), priorityList)

        jet = plt.get_cmap('Dark2')
        if self.isGrayscale():
            jet = plt.get_cmap('gray')

        cNorm = colors.Normalize(vmin=0, vmax=6)
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
        scalarMap.get_clim()

        figure1 = None
        if boxPlot:
            # Create Boxplots
            if(self.overrideWidthHeight.get() == 1):
                figure1 = plt.Figure(
                    figsize=(int(self.varWidth.get()), int(self.varHeight.get())), dpi=int(self.varDPI.get()))
            else:
                self.varWidth.set(20)
                self.varHeight.set(5)
                self.varDPI.set(100)
                figure1 = plt.Figure(figsize=(20, 5), dpi=100)

            self.plot_createBarPlot("NBS (highest-best)", figure1, 141, self.samplingFrame.getAverageData(
            ), 'Algorithm', 'Prioritization', 'NBS', scalarMap)
            self.plot_createBarPlot("SRBS (lowest-best)", figure1, 142, self.samplingFrame.getAverageData(
            ), 'Algorithm', 'Prioritization', 'SRBS', scalarMap)
            self.plot_createBarPlot("WRBS (lowest-best)", figure1, 143, self.samplingFrame.getAverageData(
            ), 'Algorithm', 'Prioritization', 'WRBS', scalarMap)
            self.plot_createBarPlot("IWRBS (highest-best)", figure1, 144, self.samplingFrame.getAverageData(
            ), 'Algorithm', 'Prioritization', 'IWRBS', scalarMap)

            bar = FigureCanvasTkAgg(figure1, self.plotFrame)
            bar.draw()
            bar.get_tk_widget().pack()
        else:
            # Determine the axis title
            title = "Prioritization " + \
                priorityList[0].printExlusively(variable)
            ticks = []
            if variable == "size":
                title = title + " with variable S"
                for prio in priorityList:
                    ticks.append(prio.size)
            elif variable == "time":
                title = title + " with variable T"
                for prio in priorityList:
                    ticks.append(prio.time)
            elif variable == "coverage":
                title = title + " with variable S"
                for prio in priorityList:
                    ticks.append(prio.coverage)
            elif variable == "similarity":
                title = title + " with variable C"
                for prio in priorityList:
                    ticks.append(prio.similarity)
            elif variable == "memory":
                title = title + " with variable Sim"
                for prio in priorityList:
                    ticks.append(prio.memory)

            # Create scatter
            if(self.overrideWidthHeight.get() == 1):
                figure1 = plt.Figure(
                    figsize=(int(self.varWidth.get()), int(self.varHeight.get())), dpi=int(self.varDPI.get()))
            else:
                self.varWidth.set(20)
                self.varHeight.set(4)
                self.varDPI.set(100)
                figure1 = plt.Figure(figsize=(20, 4), dpi=100)

            subplot = self.plot_createPlot("NBS (highest-best)", figure1, 141, self.samplingFrame.getAverageData(
            ), 'Algorithm', 'Prioritization', 'NBS', scalarMap)
            subplot.set_xlabel(title)
            subplot.xaxis.set(ticks=range(0, len(priorityList)),
                              ticklabels=ticks)
            subplot = self.plot_createPlot("SRBS (lowest-best)", figure1, 142, self.samplingFrame.getAverageData(
            ), 'Algorithm', 'Prioritization', 'SRBS', scalarMap)
            subplot.set_xlabel(title)
            subplot.xaxis.set(ticks=range(0, len(priorityList)),
                              ticklabels=ticks)
            subplot = self.plot_createPlot("WRBS (lowest-best)", figure1, 143, self.samplingFrame.getAverageData(
            ), 'Algorithm', 'Prioritization', 'WRBS', scalarMap)
            subplot.set_xlabel(title)
            subplot.xaxis.set(ticks=range(0, len(priorityList)),
                              ticklabels=ticks)
            subplot = self.plot_createPlot("IWRBS (highest-best)", figure1, 144, self.samplingFrame.getAverageData(
            ), 'Algorithm', 'Prioritization', 'IWRBS', scalarMap)
            subplot.set_xlabel(title)
            subplot.xaxis.set(ticks=range(0, len(priorityList)),
                              ticklabels=ticks)

            if(self.overrideLeftRight.get() == 1):
                figure1.subplots_adjust(left=float(
                    self.varLeft.get()), right=float(self.varRight.get()))
            else:
                self.varLeft.set(0.15)
                self.varRight.set(0.99)
                figure1.subplots_adjust(left=float(
                    self.varLeft.get()), right=float(self.varRight.get()))

            if(self.overrideTopBottom.get() == 1):
                figure1.subplots_adjust(top=float(
                    self.varTop.get()), bottom=float(self.varBottom.get()))
            else:
                self.varTop.set(0.9)
                self.varBottom.set(0.25)
                figure1.subplots_adjust(top=float(
                    self.varTop.get()), bottom=float(self.varBottom.get()))

            if(self.overrideSpace.get() == 1):
                figure1.subplots_adjust(wspace=float(
                    self.varXSpace.get()), hspace=float(self.varYSpace.get()))
            else:
                self.varXSpace.set(0.1)
                self.varYSpace.set(0.1)
                figure1.subplots_adjust(wspace=float(
                    self.varXSpace.get()), hspace=float(self.varYSpace.get()))

            # Show in UI
            scatter1 = FigureCanvasTkAgg(figure1, self.plotFrame)
            scatter1.draw()
            scatter1.get_tk_widget().pack()

        # Export
        if self.isExporting():
            figure1.savefig(self.plot_getPlotExportPath(".pdf"))

    def plot_plotRangeSize(self):
        ''' Plots all lists. '''
        # Create prioritization list
        try:
            prios = []
            startIndex = int(self.sizeVar.get())
            endIndex = int(self.sizeVarEnd.get()) + 1
            stepIncrement = int(self.sizeSteps.get())

            if startIndex >= endIndex:
                return

            for x in range(startIndex, endIndex, stepIncrement):
                prio = self.samplePrioitization.copy()
                prio.size = x
                prios.append(prio)

            self.plot_plotRangeInternal(prios, "size")
        except TclError:
            pass

    def plot_plotRangeTime(self):
        ''' Plots all lists. '''
        # Create prioritization list
        try:
            prios = []
            startIndex = int(self.timeVar.get())
            endIndex = int(self.timeVarEnd.get()) + 1
            stepIncrement = int(self.sizeSteps.get())

            if startIndex >= endIndex:
                return

            for x in range(startIndex, endIndex, stepIncrement):
                prio = self.samplePrioitization.copy()
                prio.time = x
                prios.append(prio)

            self.plot_plotRangeInternal(prios, "time")
        except TclError:
            pass

    def plot_plotRangeCoverage(self):
        ''' Plots all lists. '''
        # Create prioritization list
        try:
            prios = []
            startIndex = int(self.coverageVar.get())
            endIndex = int(self.coverageVarEnd.get()) + 1
            stepIncrement = int(self.sizeSteps.get())

            if startIndex >= endIndex:
                return

            for x in range(startIndex, endIndex, stepIncrement):
                prio = self.samplePrioitization.copy()
                prio.coverage = x
                prios.append(prio)

            self.plot_plotRangeInternal(prios, "coverage")
        except TclError:
            pass

    def plot_plotRangeSimilarity(self):
        ''' Plots all lists. '''
        # Create prioritization list
        try:
            prios = []
            startIndex = int(self.similarityVar.get())
            endIndex = int(self.similarityVarEnd.get()) + 1
            stepIncrement = int(self.sizeSteps.get())

            if startIndex >= endIndex:
                return

            for x in range(startIndex, endIndex, stepIncrement):
                prio = self.samplePrioitization.copy()
                prio.similarity = x
                prios.append(prio)

            self.plot_plotRangeInternal(prios, "similarity")
        except TclError:
            pass

    def plot_plotRangeMemory(self):
        ''' Plots all lists. '''
        # Create prioritization list
        try:
            prios = []
            startIndex = int(self.memoryVar.get())
            endIndex = int(self.memoryVarEnd.get()) + 1
            stepIncrement = int(self.sizeSteps.get())

            if startIndex >= endIndex:
                return

            for x in range(startIndex, endIndex, stepIncrement):
                prio = self.samplePrioitization.copy()
                prio.memory = x
                prios.append(prio)

            self.plot_plotRangeInternal(prios, "memory")
        except TclError:
            pass

    def plot_createPlot(self, title, figure, subplotID, dataFrame, filterUnqiue, xaxis, yaxis, scalarMap):
        ''' Creates a plot that shows the given data '''
        # Create subplot
        plot = figure.add_subplot(subplotID)

        # Extract list of uniques
        uniques = dataFrame[filterUnqiue].unique()

        if self.isLogarithmicMode():
            plot.set_yscale('log')
            plot.set_ylabel('logarithmic scale')
        if self.isGridMode():
            plot.grid()

        colorIndex = 0
        for unique in uniques:
            # Create filtered data
            filteredData = dataFrame[(dataFrame[filterUnqiue] == unique)]
            t = mpl.markers.MarkerStyle(marker='x')
            t._transform = t.get_transform().rotate_deg((90/len(uniques)) * colorIndex)
            plot.scatter(filteredData[xaxis],
                         filteredData[yaxis], marker=t, s=45, color=scalarMap.to_rgba(colorIndex))
            colorIndex = colorIndex + 1

        plot.tick_params(axis='y',
                         direction='inout',
                         length=10)
        plot.legend(uniques)
        plot.set_xlabel(xaxis)
        plot.set_title(title)
        return plot

    def plot_createComparePlot(self, title, figure, subplotID, dataFrame, filterUnqiue, xaxis, yaxis, scalarMap):
        ''' Creates a plot that shows the given data '''
        # Create subplot
        plot = figure.add_subplot(subplotID)

        # Extract list of uniques
        uniques = dataFrame[filterUnqiue].unique()
        filteredDataFrame = dataFrame[dataFrame[yaxis] != -1]
        if(yaxis == "Sample Size"):
            filteredDataFrame = filteredDataFrame[filteredDataFrame[yaxis] != 0]

        if self.isLogarithmicMode():
            plot.set_yscale('log')
            plot.set_ylabel('logarithmic scale')
        if self.isGridMode():
            plot.grid()

        colorIndex = 0
        for unique in uniques:
            # Create filtered data
            filteredData = filteredDataFrame[(
                filteredDataFrame[filterUnqiue] == unique)]
            filteredData = filteredData[filteredData[yaxis] >= 0]
            filteredData = filteredDataFrame[(
                filteredDataFrame[filterUnqiue] == unique)]
            t = mpl.markers.MarkerStyle(marker='x')
            t._transform = t.get_transform().rotate_deg((90/len(uniques)) * colorIndex)
            plot.scatter(filteredData[xaxis],
                         filteredData[yaxis], marker=t, s=45, color=scalarMap.to_rgba(colorIndex))
            colorIndex = colorIndex + 1

        plot.tick_params(axis='y',
                         direction='inout',
                         length=10)
        plot.legend(uniques)
        plot.set_xlabel(xaxis)
        plot.set_title(title)
        return plot

    def plot_createBarPlot(self, title, figure, subplotID, dataFrame, filterUnqiue, xaxis, yaxis, scalarMap):
        ''' Creates a plot that shows the given data '''
        # Create subplot
        plot = figure.add_subplot(subplotID)

        # Extract list of uniques
        uniques = dataFrame[filterUnqiue].unique()

        if self.isLogarithmicMode():
            plot.set_yscale('log')
            plot.set_ylabel('logarithmic scale')
        if self.isGridMode():
            plot.grid()

        colorIndex = 0
        for unique in uniques:
            filteredData = dataFrame[(
                dataFrame[filterUnqiue] == unique)][yaxis]
            vaules = filteredData.values.tolist()
            plot.bar(colorIndex, vaules, label=unique,
                     color=scalarMap.to_rgba(colorIndex))
            colorIndex = colorIndex + 1

        plot.xaxis.set(ticks=range(0, len(uniques)),
                       ticklabels=uniques)
        plot.tick_params(axis='y',
                         direction='inout',
                         length=10)
        plot.set_title(title + "\n" + str(dataFrame[xaxis].values.tolist()[0]))
        plot.legend(uniques)

        figure.autofmt_xdate(rotation=70)

        if(self.overrideLeftRight.get() == 1):
            figure.subplots_adjust(left=float(
                self.varLeft.get()), right=float(self.varRight.get()))
        else:
            self.varLeft.set(0.07)
            self.varRight.set(0.99)
            figure.subplots_adjust(left=float(
                self.varLeft.get()), right=float(self.varRight.get()))

        if(self.overrideTopBottom.get() == 1):
            figure.subplots_adjust(top=float(
                self.varTop.get()), bottom=float(self.varBottom.get()))
        else:
            self.varTop.set(0.9)
            self.varBottom.set(0.22)
            figure.subplots_adjust(top=float(
                self.varTop.get()), bottom=float(self.varBottom.get()))

        if(self.overrideSpace.get() == 1):
            figure.subplots_adjust(wspace=float(
                self.varXSpace.get()), hspace=float(self.varYSpace.get()))
        else:
            self.varXSpace.set(0.22)
            self.varYSpace.set(0.1)
            figure.subplots_adjust(wspace=float(
                self.varXSpace.get()), hspace=float(self.varYSpace.get()))

        return plot

    def plot_removePlots(self):
        ''' Removes all plots. '''
        self.plotFrame.destroy()
        self.setupContent_RightToolFrame()

    def plot_getPlotExportPath(self, extension):
        ''' Opens a file dialog to choose an export path. '''
        format_str = "%Y_%b_%d_%H_%M_%S"
        result = datetime.now().strftime(format_str)
        plotName = self.labelPlotName.get("1.0", END).rstrip()
        plotName = plotName + '_' + result
        # plotName = str.replace("\n", "")TODO
        file_path = os.path.join(self.args.output, "plots")
        Path(file_path).mkdir(parents=True, exist_ok=True)
        file_path = os.path.join(file_path, plotName + extension)
        return file_path

    def isExporting(self):
        return self.labelPlotName.get(
            "1.0", END) is not "\n" and self.labelPlotName.get("1.0", END) is not ""

    def isGrayscale(self):
        return self.grayscaleMode.get() == 1

    def isLogarithmicMode(self):
        return self.logarithmicMode.get() == 1

    def isGridMode(self):
        return self.gridMode.get() == 1

    def data_importDataFromInputPath(self):
        ''' Import all data from the input path. '''
        # Generate and load data
        self.samplingFrame.load(self.args.input)
        # Save generated data to disk
        self.samplingFrame.save(os.path.join(self.args.output, "data"))
        # Update data info
        self.update_DataInfo()

    def update_DataInfo(self):
        ''' Updates the information about the sampling data in the UI. '''
        if self.samplingFrame == None or len(self.samplingFrame.data) == 0:
            # Case: No data loaded
            style = Style()
            style.configure("BW.TLabel", foreground="red")
            self.labelDataStatusValue.config(
                text="No valid Data found!", style="BW.TLabel")
            self.labelDataEntriesValue.config(text="")
            self.labelDataAlgorithmsValue.config(text="")
        else:
            # Case: data loaded
            style = Style()
            style.configure("BW.TLabel", foreground="green")
            self.labelDataStatusValue.config(
                text="Data loaded!", style="BW.TLabel")
            self.labelDataEntriesValue.config(
                text=str(len(self.samplingFrame.data)))
            self.labelDataAlgorithmsValue.config(
                text=self.samplingFrame.data['Algorithm'].unique())

    def update_SizePriority(self):
        ''' Updates the information about the sampling size priority in the UI. '''
        try:
            # Update variable
            try:
                self.samplePrioitization.size = self.sizeVar.get()
            except TclError:
                return

            print("Updated the size priority to: " +
                  str(self.samplePrioitization.size))
        except TclError:
            print("Oops!  That was no valid number.  Try again...")

    def update_TimePriority(self):
        ''' Updates the information about the sampling time priority in the UI. '''
        try:
            # Update variable
            try:
                self.samplePrioitization.time = self.timeVar.get()
            except TclError:
                return
            print("Updated the time priority to: " +
                  str(self.samplePrioitization.time))
        except TclError:
            print("Oops!  That was no valid number.  Try again...")

    def update_CoveragePriority(self):
        ''' Updates the information about the sampling coverage priority in the UI. '''
        try:
            # Update variable
            try:
                self.samplePrioitization.coverage = self.coverageVar.get()
            except TclError:
                return
            print("Updated the coverage priority to: " +
                  str(self.samplePrioitization.coverage))
        except TclError:
            print("Oops!  That was no valid number.  Try again...")

    def update_SimilarityPriority(self):
        ''' Updates the information about the sampling similarity priority in the UI. '''
        try:
            # Update variable
            try:
                self.samplePrioitization.similarity = self.similarityVar.get()
            except TclError:
                return
            print("Updated the similarity priority to: " +
                  str(self.samplePrioitization.similarity))
        except TclError:
            print("Oops!  That was no valid number.  Try again...")

    def update_MemoryPriority(self):
        ''' Updates the information about the sampling memory priority in the UI. '''
        try:
            # Update variable
            try:
                self.samplePrioitization.memory = self.memoryVar.get()
            except TclError:
                return
            print("Updated the memory priority to: " +
                  str(self.samplePrioitization.memory))
        except TclError:
            print("Oops!  That was no valid number.  Try again...")

    def openInputFolder(self):
        ''' Opens the explorer showing the folder containing the input data. '''
        subprocess.Popen('explorer ' + self.args.input)

    def openExportFolder(self):
        ''' Opens the explorer showing the folder containing the exported plots. '''
        subprocess.Popen(
            'explorer ' + os.path.join(self.args.output, "plots"))

    def openOutputFolder(self):
        ''' Opens the explorer showing the folder containing the evaluation results. '''
        subprocess.Popen('explorer ' + self.args.output)

    def setupContent_ButtonMenu(self, master):
        ''' Create a menu item with the following entires: (input, reload, export, quit). '''
        self.menubar = Menu(self.frame)
        self.menubar.add_command(label="Exit", command=self.frame.quit)

    def setupContent_LeftToolFrame(self):
        ''' Creates a tool frame containing tools about changing the prios or plotting the data. '''
        toolFrame = Frame(self.frame)
        toolFrame.grid(row=0, column=0, sticky="n")

        frameStyle = Style()
        frameStyle.configure("BW.TLabelFrame", foreground="red")
        frameRow = 0
        # ----------------------------------------------------------------------------------------------------------------
        # Create frame for priorities
        # ----------------------------------------------------------------------------------------------------------------
        prioritiesFrame = LabelFrame(toolFrame, text="Prioritizations")
        prioritiesFrame.grid(row=frameRow, column=0,
                             sticky="wens", pady=10, padx=10)

        row = 0

        # Add steps field
        self.sizeSteps = DoubleVar()
        self.sizeSteps.set(1)
        Label(prioritiesFrame, text="Steps for range:").\
            grid(row=row, column=0, sticky="w")
        Spinbox(prioritiesFrame, textvariable=self.sizeSteps, from_=-1000, to_=1000).\
            grid(row=row, column=1, columnspan=4, sticky="e")
        row += 1

        # Add Size
        self.sizeVar = DoubleVar()
        self.sizeVar.set(self.samplePrioitization.size)
        self.sizeVarEnd = DoubleVar()
        self.sizeVarEnd.set(0)
        self.sizeVar.trace_add("write", lambda var, indx,
                               mode: self.update_SizePriority())
        Label(prioritiesFrame, text="Size").\
            grid(row=row, column=0, sticky="w")
        Spinbox(prioritiesFrame, textvariable=self.sizeVar, from_=-1000, to_=1000).\
            grid(row=row, column=1)
        Label(prioritiesFrame, text=" - ").\
            grid(row=row, column=2)
        Spinbox(prioritiesFrame, textvariable=self.sizeVarEnd, from_=-1000, to_=1000).\
            grid(row=row, column=3)
        Button(prioritiesFrame, text="Plot Range", command=lambda: self.plot_plotRangeSize()).\
            grid(row=row, column=4, sticky="e")
        row += 1

        # Add Time
        self.timeVar = DoubleVar()
        self.timeVar.set(self.samplePrioitization.time)
        self.timeVarEnd = DoubleVar()
        self.timeVarEnd.set(0)
        self.timeVar.trace_add("write", lambda var, indx,
                               mode: self.update_TimePriority())
        Label(prioritiesFrame, text="Time").\
            grid(row=row, column=0, sticky="w")
        Spinbox(prioritiesFrame, textvariable=self.timeVar, from_=-1000, to_=1000).\
            grid(row=row, column=1)
        Label(prioritiesFrame, text=" - ").\
            grid(row=row, column=2)
        Spinbox(prioritiesFrame, textvariable=self.timeVarEnd, from_=-1000, to_=1000).\
            grid(row=row, column=3)
        Button(prioritiesFrame, text="Plot Range", command=lambda: self.plot_plotRangeTime()).\
            grid(row=row, column=4, sticky="e")
        row += 1

        # Add Coverage
        self.coverageVar = DoubleVar()
        self.coverageVar.set(self.samplePrioitization.coverage)
        self.coverageVarEnd = DoubleVar()
        self.coverageVarEnd.set(0)
        self.coverageVar.trace_add("write", lambda var, indx,
                                   mode: self.update_CoveragePriority())
        Label(prioritiesFrame, text="Coverage").\
            grid(row=row, column=0, sticky="w")
        Spinbox(prioritiesFrame, textvariable=self.coverageVar, from_=-1000, to_=1000).\
            grid(row=row, column=1)
        Label(prioritiesFrame, text=" - ").\
            grid(row=row, column=2)
        Spinbox(prioritiesFrame, textvariable=self.coverageVarEnd, from_=-1000, to_=1000).\
            grid(row=row, column=3)
        Button(prioritiesFrame, text="Plot Range", command=lambda: self.plot_plotRangeCoverage()).\
            grid(row=row, column=4, sticky="e")
        row += 1

        # Add Similarity
        self.similarityVar = DoubleVar()
        self.similarityVar.set(self.samplePrioitization.similarity)
        self.similarityVarEnd = DoubleVar()
        self.similarityVarEnd.set(0)
        self.similarityVar.trace_add("write", lambda var, indx,
                                     mode: self.update_SimilarityPriority())
        Label(prioritiesFrame, text="Similarity").\
            grid(row=row, column=0, sticky="w")
        Spinbox(prioritiesFrame, textvariable=self.similarityVar, from_=-1000, to_=1000).\
            grid(row=row, column=1)
        Label(prioritiesFrame, text=" - ").\
            grid(row=row, column=2)
        Spinbox(prioritiesFrame, textvariable=self.similarityVarEnd, from_=-1000, to_=1000).\
            grid(row=row, column=3)
        Button(prioritiesFrame, text="Plot Range", command=lambda: self.plot_plotRangeSimilarity()).\
            grid(row=row, column=4, sticky="e")
        row += 1

        # Add Memory
        self.memoryVar = DoubleVar()
        self.memoryVar.set(self.samplePrioitization.memory)
        self.memoryVarEnd = DoubleVar()
        self.memoryVarEnd.set(0)
        self.memoryVar.trace_add("write", lambda var, indx,
                                 mode: self.update_MemoryPriority())
        Label(prioritiesFrame, text="Memory").\
            grid(row=row, column=0, sticky="w")
        Spinbox(prioritiesFrame, textvariable=self.memoryVar, from_=-1000, to_=1000).\
            grid(row=row, column=1)
        Label(prioritiesFrame, text=" - ").\
            grid(row=row, column=2)
        Spinbox(prioritiesFrame, textvariable=self.memoryVarEnd, from_=-1000, to_=1000).\
            grid(row=row, column=3)
        Button(prioritiesFrame, text="Plot Range", command=lambda: self.plot_plotRangeMemory()).\
            grid(row=row, column=4, sticky="e")
        row += 1

        buttonAddToList = Button(
            prioritiesFrame, text="Add to list", command=self.plot_addToList)
        buttonAddToList.grid(row=row, columnspan=5, sticky="wens")
        row += 1

        labelEvalList = Label(prioritiesFrame, text="Plot List")
        labelEvalList.grid(row=row, columnspan=5, sticky="wens")
        row += 1
        self.listEvalList = Listbox(prioritiesFrame, width=20, height=4)
        self.listEvalList.grid(row=row, columnspan=5, sticky="wens")
        row += 1

        buttonClearList = Button(
            prioritiesFrame, text="Clear list", command=self.plot_clearList)
        buttonClearList.grid(row=row, columnspan=5, sticky="we")
        row += 1

        buttonPlotPrio = Button(
            prioritiesFrame, text="Plot list", command=lambda: self.plot_plotList())
        buttonPlotPrio.grid(row=row, columnspan=5, sticky="wens")
        row += 1

        buttonClearPlots = Button(
            prioritiesFrame, text="Delete plot", command=self.plot_removePlots)
        buttonClearPlots.grid(row=row, columnspan=5, sticky="wens")
        row += 1
        # ----------------------------------------------------------------------------------------------------------------
        # Create frame for comparison self, title, xtitle, xaxis, ytitle, yaxis
        # ----------------------------------------------------------------------------------------------------------------
        frameRow += 1
        comparisonFrame = LabelFrame(toolFrame, text="Comparison")
        comparisonFrame.grid(row=frameRow, column=0,
                             sticky="wens", pady=10, padx=10)

        Button(comparisonFrame, text="Size", command=lambda: self.plot_plotComparison(
            'Sample Size',
            'number of features',
            'System Features',
            'size',
            'Sample Size')).\
            grid(row=row, column=0)
        Button(comparisonFrame, text="Time", command=lambda: self.plot_plotComparison(
            'Sample Time',
            'number of features',
            'System Features',
            'time',
            'Sample Time')).\
            grid(row=row, column=1)
        Button(comparisonFrame, text="Coverage", command=lambda: self.plot_plotComparison(
            'Sample Coverage',
            'number of features',
            'System Features',
            'coverage',
            'Sample Coverage')).\
            grid(row=row, column=2)
        Button(comparisonFrame, text="Similarity", command=lambda: self.plot_plotComparison(
            'Sample Similarity',
            'number of features',
            'System Features',
            'similarity',
            'Sample Similarity')).\
            grid(row=row, column=3)
        Button(comparisonFrame, text="Memory", command=lambda: self.plot_plotComparison(
            'Sample Memory',
            'number of features',
            'System Features',
            'consumed memory',
            'Sample Memory')).\
            grid(row=row, column=4)
        # ----------------------------------------------------------------------------------------------------------------
        # Create frame for plot options
        # ----------------------------------------------------------------------------------------------------------------
        frameRow += 1
        plotOptionFrame = LabelFrame(toolFrame, text="Plot Options")
        plotOptionFrame.grid(row=frameRow, column=0,
                             sticky="wens", pady=10, padx=10)

        row = 0
        labelPlotNameLabel = Label(plotOptionFrame, text=("Plot Name:"))
        labelPlotNameLabel.grid(row=row, column=0, sticky="w")
        self.labelPlotName = Text(plotOptionFrame, height=1, width=20)
        self.labelPlotName.grid(row=row, column=1, columnspan=4, sticky="we")
        row += 1

        self.grayscaleMode = IntVar()
        grayscaleModeButton = Checkbutton(
            plotOptionFrame, text="Grayscale Mode", variable=self.grayscaleMode)
        grayscaleModeButton.grid(row=row, columnspan=4, sticky="wens")
        row += 1

        self.logarithmicMode = IntVar()
        logarithmicModeButton = Checkbutton(
            plotOptionFrame, text="Logarithmic Scale", variable=self.logarithmicMode)
        logarithmicModeButton.grid(row=row, columnspan=4, sticky="wens")
        row += 1

        self.gridMode = IntVar()
        gridModeButton = Checkbutton(
            plotOptionFrame, text="Draw Grid", variable=self.gridMode)
        gridModeButton.grid(row=row, columnspan=4, sticky="wens")
        row += 1

        # Figure Size
        self.overrideWidthHeight = IntVar()
        self.overrideWidthHeight.set(0)
        self.varWidth = DoubleVar()
        self.varWidth.set(0)
        self.varHeight = DoubleVar()
        self.varHeight.set(0)
        self.varDPI = DoubleVar()
        self.varDPI.set(0)
        Checkbutton(
            plotOptionFrame, text="Override Width/Height & DPI", variable=self.overrideWidthHeight).\
            grid(row=row, column=0, sticky="w")
        Spinbox(plotOptionFrame, textvariable=self.varWidth, width=10).\
            grid(row=row, column=1)
        Spinbox(plotOptionFrame, textvariable=self.varHeight, width=10).\
            grid(row=row, column=2)
        Spinbox(plotOptionFrame, textvariable=self.varDPI, width=10).\
            grid(row=row, column=3)
        row += 1

        # Figure Top/bottom
        self.overrideTopBottom = IntVar()
        self.overrideTopBottom.set(0)
        self.varTop = DoubleVar()
        self.varTop.set(0)
        self.varBottom = DoubleVar()
        self.varBottom.set(0)
        Checkbutton(
            plotOptionFrame, text="Override Top/Bottom", variable=self.overrideTopBottom).\
            grid(row=row, column=0, sticky="w")
        Spinbox(plotOptionFrame, textvariable=self.varTop, width=10).\
            grid(row=row, column=1)
        Spinbox(plotOptionFrame, textvariable=self.varBottom, width=10).\
            grid(row=row, column=2)
        row += 1

        # Figure Top/bottom
        self.overrideLeftRight = IntVar()
        self.overrideLeftRight.set(0)
        self.varLeft = DoubleVar()
        self.varLeft.set(0)
        self.varRight = DoubleVar()
        self.varRight.set(0)
        Checkbutton(
            plotOptionFrame, text="Override Left/Right", variable=self.overrideLeftRight).\
            grid(row=row, column=0, sticky="w")
        Spinbox(plotOptionFrame, textvariable=self.varLeft, width=10).\
            grid(row=row, column=1)
        Spinbox(plotOptionFrame, textvariable=self.varRight, width=10).\
            grid(row=row, column=2)
        row += 1

        # Figure Top/bottom
        self.overrideSpace = IntVar()
        self.overrideSpace.set(0)
        self.varXSpace = DoubleVar()
        self.varXSpace.set(0)
        self.varYSpace = DoubleVar()
        self.varYSpace.set(0)
        Checkbutton(
            plotOptionFrame, text="Override X/Y Space", variable=self.overrideSpace).\
            grid(row=row, column=0, sticky="w")
        Spinbox(plotOptionFrame, textvariable=self.varXSpace, width=10).\
            grid(row=row, column=1)
        Spinbox(plotOptionFrame, textvariable=self.varYSpace, width=10).\
            grid(row=row, column=2)
        row += 1
        # ----------------------------------------------------------------------------------------------------------------
        # Create frame for data info (Pack Layout)
        # ----------------------------------------------------------------------------------------------------------------
        frameRow += 1
        dataFrame = LabelFrame(toolFrame, text="Data Information")
        dataFrame.grid(row=frameRow, column=0, sticky="wens", pady=10, padx=10)
        labelDataStatus = Label(dataFrame, text="Status:")
        labelDataStatus.grid(row=0, column=0, sticky="w")
        style = Style()
        style.configure("BW.TLabel", foreground="red")
        self.labelDataStatusValue = Label(
            dataFrame, text="No data loaded", style="BW.TLabel")
        self.labelDataStatusValue.grid(row=0, column=1)

        labelDataEntries = Label(dataFrame, text="Number of Entries:")
        labelDataEntries.grid(row=1, column=0, sticky="w")
        self.labelDataEntriesValue = Label(dataFrame, text="")
        self.labelDataEntriesValue.grid(row=1, column=1)

        labelDataAlgorithms = Label(dataFrame, text="Algorithms:")
        labelDataAlgorithms.grid(row=2, column=0, sticky="w")
        self.labelDataAlgorithmsValue = Label(dataFrame, text="")
        self.labelDataAlgorithmsValue.grid(row=2, column=1)

        # ----------------------------------------------------------------------------------------------------------------
        # Create frame for data import(Pack Layout)
        # ----------------------------------------------------------------------------------------------------------------
        frameRow += 1
        importFrame = LabelFrame(toolFrame, text="Import")
        importFrame.grid(row=frameRow, column=0,
                         sticky="wens", pady=10, padx=10)

        # Handle import of data
        buttonCreateDataFromInputFolder = Button(
            importFrame, text="Load Data", command=self.data_importDataFromInputPath)
        buttonCreateDataFromInputFolder.pack(fill=X)

        # ----------------------------------------------------------------------------------------------------------------
        # Create frame for data loading (Pack Layout)
        # ----------------------------------------------------------------------------------------------------------------
        frameRow += 1
        pathFrames = LabelFrame(toolFrame, text="Paths")
        pathFrames.grid(row=frameRow, column=0,
                        sticky="wens", pady=10, padx=10)

        # Handle loading of data
        buttonOpenInputFolder = Button(
            pathFrames, text="Open Input Folder", command=self.openInputFolder)
        buttonOpenInputFolder.pack(fill=X)

        buttonShowOutputMap = Button(
            pathFrames, text="Open Output Folder", command=self.openOutputFolder)
        buttonShowOutputMap.pack(fill=X)

        buttonPlotPrio = Button(
            pathFrames, text="Open Saved Plots Folder", command=lambda: self.openExportFolder())
        buttonPlotPrio.pack(fill=X)

    def setupContent_RightToolFrame(self):
        ''' Creates a plot frame '''
        self.plotFrame = Frame(self.frame)
        self.plotFrame.grid(row=0, column=1, sticky="wens")

    def __init__(self, master, args):
        self.master = master
        self.frame = Frame(master)
        self.frame.grid()

        # Setup menu
        self.setupContent_ButtonMenu(master)
        master.config(menu=self.menubar)

        # Parse arguments and extract prioritizations
        self.args = args
        self.samplePrioitization = getPrioritization(self.args)

        # Setup empty sampling frame
        self.samplingFrame = SamplingFrame()

        # Setup toolframe
        self.setupContent_RightToolFrame()
        self.setupContent_LeftToolFrame()

        # Load all data
        # self.data_importDataFromInputPath()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# Main
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
args = parseArguments()

if args.gui:
    root = Tk()
    app = RequirementEvaluator(root, args)
    root.mainloop()
else:
    # Calculate
    samplePrioitization = getPrioritization(args)
    # Setup empty sampling frame
    samplingFrame = SamplingFrame()
    # Generate and load data
    samplingFrame.load(args.input)
    # Check if data is available
    if samplingFrame.data is None or len(samplingFrame.data) == 0:
        # Case: No data available inform user
        print("No data loaded!")
    else:
        # Clean average object
        samplingFrame.average = samplingFrame.average.iloc[0:0]

        # Compute average version
        samplingFrame.getBasicAverages(samplePrioitization)

        # Compute score for each samplePrioitization
        samplingFrame.calculate_Individual(samplePrioitization)
        samplingFrame.calculate_Simple(samplePrioitization)
        samplingFrame.calculate_Weighted(samplePrioitization)
        samplingFrame.calculate_InverseWeighted(samplePrioitization)

        if args.tiraInput:
            # Setup empty sampling frame
            tiraInputFrame = SamplingFrame()
            # load data.csv from tiraInputPath
            loaded = False
            for path in Path(args.tiraInput).rglob('data.csv'):
                tiraInputFrame.load(path)
                loaded = True
                break
            if not loaded:
                print("Data.csv not found recursively at: " + args.tiraInput)
                exit()
            # Get unique
            unique = tiraInputFrame.data["Algorithm"].unique()[0]
            # Extract list of uniques
            view = samplingFrame.average[samplingFrame.average["Algorithm"] == unique]

            with open(os.path.join(args.output, "evaluation.prototext"), 'w+') as file:
                # Priority
                file.write("measure {\n")
                file.write("  key : " + "\"Prioritization\"\n")
                file.write("  value : " + "\"" +
                           str(samplePrioitization) + "\"\n")
                file.write("}\n")
                # NBS
                file.write("measure {\n")
                file.write("  key : " + "\"NBS\"\n")
                file.write("  value : " + "\"" +
                           str(view['NBS'].iloc[0]) + "\"\n")
                file.write("}\n")
                file.write("measure {\n")
                file.write("  key : " + "\"NBS Rank\"\n")
                file.write("  value : " + "\"" +
                           str(view['NBS Rank'].iloc[0]) + "\"\n")
                file.write("}\n")
                # SRBS
                file.write("measure {\n")
                file.write("  key : " + "\"SRBS\"\n")
                file.write("  value : " + "\"" +
                           str(view['SRBS'].iloc[0]) + "\"\n")
                file.write("}\n")
                file.write("measure {\n")
                file.write("  key : " + "\"SRBS Rank\"\n")
                file.write("  value : " + "\"" +
                           str(view['SRBS Rank'].iloc[0]) + "\"\n")
                file.write("}\n")
                # WRBS
                file.write("measure {\n")
                file.write("  key : " + "\"WRBS\"\n")
                file.write("  value : " + "\"" +
                           str(view['WRBS'].iloc[0]) + "\"\n")
                file.write("}\n")
                file.write("measure {\n")
                file.write("  key : " + "\"WRBS Rank\"\n")
                file.write("  value : " + "\"" +
                           str(view['WRBS Rank'].iloc[0]) + "\"\n")
                file.write("}\n")
                # IWRBS
                file.write("measure {\n")
                file.write("  key : " + "\"IWRBS \"\n")
                file.write("  value : " + "\"" +
                           str(view['IWRBS'].iloc[0]) + "\"\n")
                file.write("}\n")
                file.write("measure {\n")
                file.write("  key : " + "\"IWRBS Rank\"\n")
                file.write("  value : " + "\"" +
                           str(view['IWRBS Rank'].iloc[0]) + "\"\n")
                file.write("}\n")
                # Data Averages
                file.write("measure {\n")
                file.write("  key : " + "\"Avg. Sample Size\"\n")
                file.write("  value : " + "\"" +
                           str(view['Avg. Size'].iloc[0]) + "\"\n")
                file.write("}\n")
                file.write("measure {\n")
                file.write("  key : " + "\"Avg. Sample Time\"\n")
                file.write("  value : " + "\"" +
                           str(view['Avg. Time'].iloc[0]) + "\"\n")
                file.write("}\n")
                file.write("measure {\n")
                file.write("  key : " + "\"Avg. Sample Coverage\"\n")
                file.write("  value : " + "\"" +
                           str(view['Avg. Coverage'].iloc[0]) + "\"\n")
                file.write("}\n")
                file.write("measure {\n")
                file.write("  key : " + "\"Avg. Sample Similarity\"\n")
                file.write("  value : " + "\"" +
                           str(view['Avg. Similarity'].iloc[0]) + "\"\n")
                file.write("}\n")
                file.write("measure {\n")
                file.write("  key : " + "\"Avg. Sample Memory\"\n")
                file.write("  value : " + "\"" +
                           str(view['Avg. Memory'].iloc[0]) + "\"\n")
                file.write("}\n")
        else:
            print("\nResults for "+str(samplePrioitization)+":")
            pd.set_option('display.max_colwidth', None)
            print(samplingFrame.average[[
                  "Algorithm", "NBS", "NBS Rank", "SRBS", "SRBS Rank", "WRBS", "WRBS Rank", "IWRBS", "IWRBS Rank", 'Avg. Size', 'Avg. Time', 'Avg. Coverage', 'Avg. Similarity', 'Avg. Memory']])
            print(samplingFrame.average[[
                  "Algorithm", 'Avg. Size', 'Avg. Time', 'Avg. Coverage', 'Avg. Similarity', 'Avg. Memory']])
