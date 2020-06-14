import sd_core as sd
# Others
import os
import glob
# For parsing arguments
import argparse
# For opening respective folders
import subprocess
# For plotting
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
# For timestamping files
from datetime import datetime
import time
# Tkinter + Plotting
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd

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
    parser.add_argument('--mode',
                        type=str,
                        choices=["SRBS", "WRBS", "IWRBS", "NBS", "all"],
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
    return parser.parse_args()


def getPrioritization(arguments):
    # Get size
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
    return sd.Prioritization(size, time, coverage, similarity, memory)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# Programm Class
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class RequirementEvaluator:
    ''' The graphical class of our requirements evaluator. '''
    # UI Variables
    master = None
    frame = Frame
    menubar = Menu
    labelDataStatusValue, labelDataEntriesValue, labelDataAlgorithmsValue = Label, Label, Label
    listEvalList = Listbox
    labelPlotName = Text
    plotFrame = Frame
    grayscaleMode, logarithmicMode, gridMode = IntVar, IntVar, IntVar
    xSpace, ySpace = DoubleVar, DoubleVar
    # Data Variables
    samplingFrame = sd.SamplingFrame
    args = None
    samplePrioitization = sd.Prioritization
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

            jet = plt.get_cmap('jet')
            if self.isGrayscale():
                jet = plt.get_cmap('Greys')

            cNorm = colors.Normalize(vmin=0, vmax=4)
            scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
            scalarMap.get_clim()

            # Boxplot when only one priority
            if boxPlot:
                # Create Boxplots
                figure1 = plt.Figure(figsize=(20, 5), dpi=100)
                self.plot_createBarPlot("NBS (highest-best)", figure1, 141, self.samplingFrame.getAverageData(
                ), 'Algorithm', True, 'Prioritization', 'NBS', scalarMap)
                self.plot_createBarPlot("SRBS (lowest-best)", figure1, 142, self.samplingFrame.getAverageData(
                ), 'Algorithm', True, 'Prioritization', 'SRBS', scalarMap)
                self.plot_createBarPlot("WRBS (lowest-best)", figure1, 143, self.samplingFrame.getAverageData(
                ), 'Algorithm', True, 'Prioritization', 'WRBS', scalarMap)
                self.plot_createBarPlot("IWRBS (highest-best)", figure1, 144, self.samplingFrame.getAverageData(
                ), 'Algorithm', True, 'Prioritization', 'IWRBS', scalarMap)

                figure1.autofmt_xdate(rotation=70)
                figure1.subplots_adjust(
                    bottom=0.25, top=0.9, left=0.1, right=0.99)

                if(self.isYSpace()):
                    figure1.subplots_adjust(hspace=float(self.ySpace.get()))
                if(self.isXSpace()):
                    figure1.subplots_adjust(wspace=float(self.xSpace.get()))

                # Export
                if self.isExporting():
                    figure1.savefig(self.plot_getPlotExportPath(".pdf"))

                bar = FigureCanvasTkAgg(figure1, self.plotFrame)
                bar.draw()
                bar.get_tk_widget().pack()
            else:
                # Create scatter
                figure1 = plt.Figure(figsize=(20, 6), dpi=100)
                self.plot_createPlot("NBS (highest-best)", figure1, 141, self.samplingFrame.getAverageData(
                ), 'Algorithm', True, 'Prioritization', 'NBS', scalarMap)
                self.plot_createPlot("SRBS (lowest-best)", figure1, 142, self.samplingFrame.getAverageData(
                ), 'Algorithm', True, 'Prioritization', 'SRBS', scalarMap)
                self.plot_createPlot("WRBS (lowest-best)", figure1, 143, self.samplingFrame.getAverageData(
                ), 'Algorithm', True, 'Prioritization', 'WRBS', scalarMap)
                self.plot_createPlot("IWRBS (highest-best)", figure1, 144, self.samplingFrame.getAverageData(
                ), 'Algorithm', True, 'Prioritization', 'IWRBS', scalarMap)

                figure1.autofmt_xdate(rotation=70)
                figure1.subplots_adjust(
                    bottom=0.4, top=0.93, left=0.05, right=0.95)

                if(self.isYSpace()):
                    figure1.subplots_adjust(hspace=float(self.ySpace.get()))
                if(self.isXSpace()):
                    figure1.subplots_adjust(wspace=float(self.xSpace.get()))

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

        jet = plt.get_cmap('jet')
        if self.isGrayscale():
            jet = plt.get_cmap('Greys')

        cNorm = colors.Normalize(vmin=0, vmax=4)
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
        scalarMap.get_clim()

        if boxPlot:
            # Create Boxplots
            figure1 = plt.Figure(figsize=(20, 5), dpi=100)
            self.plot_createBarPlot("NBS (highest-best)", figure1, 141, self.samplingFrame.getAverageData(
            ), 'Algorithm', True, 'Prioritization', 'NBS', scalarMap)
            self.plot_createBarPlot("SRBS (lowest-best)", figure1, 142, self.samplingFrame.getAverageData(
            ), 'Algorithm', True, 'Prioritization', 'SRBS', scalarMap)
            self.plot_createBarPlot("WRBS (lowest-best)", figure1, 143, self.samplingFrame.getAverageData(
            ), 'Algorithm', True, 'Prioritization', 'WRBS', scalarMap)
            self.plot_createBarPlot("IWRBS (highest-best)", figure1, 144, self.samplingFrame.getAverageData(
            ), 'Algorithm', True, 'Prioritization', 'IWRBS', scalarMap)

            figure1.autofmt_xdate(rotation=70)
            figure1.subplots_adjust(
                bottom=0.25, top=0.9, left=0.1, right=0.99)

            if(self.isYSpace()):
                figure1.subplots_adjust(hspace=float(self.ySpace.get()))
            if(self.isXSpace()):
                figure1.subplots_adjust(wspace=float(self.xSpace.get()))

            # Export
            if self.isExporting():
                figure1.savefig(self.plot_getPlotExportPath(".pdf"))

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
            figure1 = plt.Figure(figsize=(20, 4), dpi=100)
            subplot = self.plot_createPlot("NBS (highest-best)", figure1, 141, self.samplingFrame.getAverageData(
            ), 'Algorithm', True, 'Prioritization', 'NBS', scalarMap)
            subplot.set_xlabel(title)
            subplot.xaxis.set(ticks=range(0, len(priorityList)),
                              ticklabels=ticks)
            subplot = self.plot_createPlot("SRBS (lowest-best)", figure1, 142, self.samplingFrame.getAverageData(
            ), 'Algorithm', True, 'Prioritization', 'SRBS', scalarMap)
            subplot.set_xlabel(title)
            subplot.xaxis.set(ticks=range(0, len(priorityList)),
                              ticklabels=ticks)
            subplot = self.plot_createPlot("WRBS (lowest-best)", figure1, 143, self.samplingFrame.getAverageData(
            ), 'Algorithm', True, 'Prioritization', 'WRBS', scalarMap)
            subplot.set_xlabel(title)
            subplot.xaxis.set(ticks=range(0, len(priorityList)),
                              ticklabels=ticks)
            subplot = self.plot_createPlot("IWRBS (highest-best)", figure1, 144, self.samplingFrame.getAverageData(
            ), 'Algorithm', True, 'Prioritization', 'IWRBS', scalarMap)
            subplot.set_xlabel(title)
            subplot.xaxis.set(ticks=range(0, len(priorityList)),
                              ticklabels=ticks)

            # Export
            if self.isExporting():
                figure1.savefig(self.plot_getPlotExportPath(".pdf"))

            figure1.subplots_adjust(
                bottom=0.15, top=0.93, left=0.05, right=0.95)

            if(self.isYSpace()):
                figure1.subplots_adjust(hspace=float(self.ySpace.get()))
            if(self.isXSpace()):
                figure1.subplots_adjust(wspace=float(self.xSpace.get()))

            # Show in UI
            scatter1 = FigureCanvasTkAgg(figure1, self.plotFrame)
            scatter1.draw()
            scatter1.get_tk_widget().pack()

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

    def plot_createPlot(self, title, figure, subplotID, dataFrame, filterUnqiue, filterMask, xaxis, yaxis, scalarMap):
        ''' Creates a plot that shows the given data '''
        # Create subplot
        plot = figure.add_subplot(subplotID)

        # Extract list of uniques
        uniques = dataFrame[filterUnqiue].unique()

        colorIndex = 1
        for unique in uniques:
            # Create filtered data
            filteredData = dataFrame[(dataFrame[filterUnqiue] == unique)]
            plot.scatter(filteredData[xaxis],
                         filteredData[yaxis], marker="x", color=scalarMap.to_rgba(colorIndex))
            colorIndex = colorIndex + 1

        if self.isLogarithmicMode():
            plot.set_yscale('log')
            plot.set_ylabel('logarithmic scale')
        if self.isGridMode():
            plot.grid()

        plot.tick_params(axis='y',
                         direction='inout',
                         length=10)
        plot.legend(uniques)
        plot.set_xlabel(xaxis)
        plot.set_title(title)
        return plot

    def plot_createBarPlot(self, title, figure, subplotID, dataFrame, filterUnqiue, filterMask, xaxis, yaxis, scalarMap):
        ''' Creates a plot that shows the given data '''
        # Create subplot
        plot = figure.add_subplot(subplotID)

        # Extract list of uniques
        uniques = dataFrame[filterUnqiue].unique()

        colorIndex = 1
        for unique in uniques:
            filteredData = dataFrame[(
                dataFrame[filterUnqiue] == unique)][yaxis]
            vaules = filteredData.values.tolist()
            plot.bar(colorIndex, vaules, label=unique,
                     color=scalarMap.to_rgba(colorIndex))
            colorIndex = colorIndex + 1

        if self.isLogarithmicMode():
            plot.set_yscale('log')
            plot.set_ylabel('logarithmic scale')
        if self.isGridMode():
            plot.grid()

        plot.xaxis.set(ticks=range(1, len(uniques)+1),
                       ticklabels=uniques)
        plot.tick_params(axis='y',
                         direction='inout',
                         length=10)
        plot.set_title(title + "\n" + str(dataFrame[xaxis].values.tolist()[0]))
        plot.legend(uniques)
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
        file_path = os.path.join(os.path.join(
            self.args.output, "plots"), plotName + extension)
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

    def isYSpace(self):
        if isinstance(self.ySpace.get(), float):
            return self.ySpace.get() > 0 and self.ySpace.get() <= 1

    def isXSpace(self):
        if isinstance(self.xSpace.get(), float):
            return self.xSpace.get() > 0 and self.xSpace.get() <= 1

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
            except TclError as t:
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
            except TclError as t:
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
            except TclError as t:
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
            except TclError as t:
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
            except TclError as t:
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
        # ----------------------------------------------------------------------------------------------------------------
        # Create frame for priorities
        # ----------------------------------------------------------------------------------------------------------------
        prioritiesFrame = LabelFrame(toolFrame, text="Prioritizations")
        prioritiesFrame.grid(row=0, column=0, sticky="wens", pady=10, padx=10)

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

        labelPlotNameLabel = Label(prioritiesFrame, text=("Plot Name:"))
        labelPlotNameLabel.grid(row=row, column=0, sticky="w")
        self.labelPlotName = Text(prioritiesFrame, height=1, width=20)
        self.labelPlotName.grid(row=row, column=1, columnspan=4, sticky="we")
        row += 1

        self.grayscaleMode = IntVar()
        grayscaleModeButton = Checkbutton(
            prioritiesFrame, text="Grayscale Mode", variable=self.grayscaleMode)
        grayscaleModeButton.grid(row=row, columnspan=5, sticky="wens")
        row += 1

        self.logarithmicMode = IntVar()
        logarithmicModeButton = Checkbutton(
            prioritiesFrame, text="Logarithmic Scale", variable=self.logarithmicMode)
        logarithmicModeButton.grid(row=row, columnspan=5, sticky="wens")
        row += 1

        self.gridMode = IntVar()
        gridModeButton = Checkbutton(
            prioritiesFrame, text="Draw Grid", variable=self.gridMode)
        gridModeButton.grid(row=row, columnspan=5, sticky="wens")
        row += 1

        self.xSpace = DoubleVar()
        self.xSpace.set(0)
        self.ySpace = DoubleVar()
        self.ySpace.set(0)
        Label(prioritiesFrame, text=("X/Y Space:")).\
            grid(row=row, column=0, sticky="w")
        Spinbox(prioritiesFrame, textvariable=self.xSpace).\
            grid(row=row, column=1, columnspan=2, sticky="we")
        Spinbox(prioritiesFrame, textvariable=self.ySpace).\
            grid(row=row, column=3, columnspan=2, sticky="we")
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
        # Create frame for data info (Pack Layout)
        # ----------------------------------------------------------------------------------------------------------------
        dataFrame = LabelFrame(toolFrame, text="Data Information")
        dataFrame.grid(row=1, column=0, sticky="wens", pady=10, padx=10)
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
        importFrame = LabelFrame(toolFrame, text="Import")
        importFrame.grid(row=2, column=0, sticky="wens", pady=10, padx=10)

        # Handle import of data
        buttonCreateDataFromInputFolder = Button(
            importFrame, text="Load Data", command=self.data_importDataFromInputPath)
        buttonCreateDataFromInputFolder.pack(fill=X)

        # ----------------------------------------------------------------------------------------------------------------
        # Create frame for data loading (Pack Layout)
        # ----------------------------------------------------------------------------------------------------------------
        pathFrames = LabelFrame(toolFrame, text="Paths")
        pathFrames.grid(row=3, column=0, sticky="wens", pady=10, padx=10)

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

    def __init__(self, master):
        self.master = master
        self.frame = Frame(master)
        self.frame.grid()

        # Setup menu
        self.setupContent_ButtonMenu(master)
        master.config(menu=self.menubar)

        # Parse arguments and extract prioritizations
        self.args = parseArguments()
        self.samplePrioitization = getPrioritization(self.args)

        # Setup empty sampling frame
        self.samplingFrame = sd.SamplingFrame()

        # Setup toolframe
        self.setupContent_RightToolFrame()
        self.setupContent_LeftToolFrame()

        # Load all data
        self.data_importDataFromInputPath()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# Main
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


root = Tk()
app = RequirementEvaluator(root)
root.mainloop()
