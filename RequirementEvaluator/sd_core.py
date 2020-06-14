''' This module is responsible to load and store the data for the sampling evaluator. It uses pandas data frames internally to handle the data and their mutations '''

import pandas as pd
import os
from glob import glob


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

        if os.path.isdir(absoluteInputPath):
            # Read all files and process the "input*.csv files"
            for path in glob(absoluteInputPath + "\\*.csv"):
                self.loadFromFile(path)
        elif os.path.isfile(absoluteInputPath):
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
