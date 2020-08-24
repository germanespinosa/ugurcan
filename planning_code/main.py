from game import Game
from simulator import Knowledge
from mcts import SearchParams, UnitTestMCTS
from experiment import ExperimentParams, Experiment
from entropy import UnitTestENTROPY
from utils import UnitTestUTILS
from coord import COORD, UnitTestCOORD
import json

import os, sys, itertools,  glob
from pathlib2 import Path
import numpy as np
import pandas as pd
import cPickle as pickle
from multiprocessing import Pool

#import pickle
#from mpi4py import MPI

SearchParams.Verbose = 0

XSize = 15
YSize = 15
numSimulations = 20
numEntropy = 10
numPredators = 5

treeknowlege = 2 # 0 = pure, 1 = legal, 2 = smart
rolloutknowledge = 2 # 0 = pure, 1 = legal, 2 = smart
smarttreecount = 1.0 # prior count for preferred actions in smart tree search
smarttreevalue = 1.0 # prior value for preferred actions during smart tree search

def GetOcclusions(mainDirectory):
    occlusions = np.zeros((numSimulations, numEntropy)).tolist()
    print("Importing occlusions")
    for simulation in range(numSimulations):
        for entropy in range(numEntropy):
            occlusionFile = "../simulations/Entropy_%d/OcclusionCoordinates_Simulation%d.csv" % (entropy, simulation)
            with open(occlusionFile) as f:
                lines = f.readlines()
            o = []
            for l in lines:
                if '"' not in l and 'X' not in l:
                    o += [(int(l.split(',')[0]), int(l.split(',')[1]))]

            occlusionCoordinates = [COORD(x[0], x[1]) for x in o]

            occlusions[simulation][entropy] = occlusionCoordinates
    return occlusions

def GetPredatorLocations(mainDirectory):
    predatorLocations = [[[[] for predator in range(numPredators)] for entropy in range(numEntropy)]
                       for simulation in range(numSimulations)]
    for simulation in range(numSimulations):
        for entropy in range(numEntropy):
            for predator in range(numPredators):
                try:
                    episodeFolder = mainDirectory + '/../Data_NatComm/Simulation_%d/Occlusion_%d/Predator_%d/Depth_5000/Episode_*.csv' % (
                    simulation, entropy, predator)
                    episodeFiles = glob.glob(episodeFolder)
                    episode = pd.read_csv(episodeFiles[0], header=0)
                except IndexError:
                    episodeFolder = mainDirectory + '/../Data_NatComm/Simulation_%d/Occlusion_%d/Predator_%d/Depth_1/Episode_*.csv' % (
                        simulation, entropy, predator)
                    episodeFiles = glob.glob(episodeFolder)
                    try:
                        episode = pd.read_csv(episodeFiles[0], header=0)
                    except IndexError:
                        continue

                predatorLocations[simulation][entropy][predator] = COORD(episode['Predator X'].iloc[0],
                                                                         episode['Predator Y'].iloc[0])

    return predatorLocations


def UnitTests():
    print("Testing UTILS")
    UnitTestUTILS()
    print("Testing COORD")
    UnitTestCOORD()
    print("Testing MCTS")
    UnitTestMCTS()
    print("Testing ENTROPY")
    UnitTestENTROPY()
    print("Testing complete!")

def SafeMultiExperiment(args):
    try:
        MultiExperiment(args)
    except (ValueError, IndexError) as e:
        print("Error in Simulation %d, Entropy 0.%d, Visual Range %d, Predator %d, Depth %d, Trial #%d"
              %(args[6], args[1][0], args[2], args[4][0], args[3], args[5]))

def MultiExperiment(args):
    directory = args[0]
    occlusionInd = args[1][0]
    occlusions = args[1][1]
    visualrange = args[2]
    depth = args[3]
    predatorInd = args[4][0]
    predatorHome = args[4][1]

    trial = args[5]
    simulationInd = args[6]


    print(args)
    #occlusionInd = occlusionInfo[0]
    #occlusions = occlusionInfo[1]
    #predatorInd = predatorInfo[0]
    #predatorHome = predatorInfo[1]
    #print("Simulation %d, Entropy 0.%d, Visual Range %d, Predator %d, Depth %d, Trial #%d"
    # % (simulationInd, occlusionInd, visualrange, predatorInd, depth, trial))

    real = Game(XSize, YSize)
    simulator = Game(XSize, YSize)

    knowledge = Knowledge()
    knowledge.TreeLevel = treeknowlege
    knowledge.RolloutLevel = rolloutknowledge
    knowledge.SmartTreeCount = smarttreecount
    knowledge.SmartTreeValue = smarttreevalue

    experiment = Experiment(real, simulator)
    simulationDirectory = directory + '/Data/Simulation_%d_Entropy_%d'%(simulationInd, occlusionInd)
    Path(simulationDirectory).mkdir(parents=True, exist_ok=True)

    _ = experiment.DiscountedReturn(occlusions, visualrange, predatorHome, depth, knowledge,
                                    occlusionInd, predatorInd, trial, simulationDirectory)


def MPITest(args):
    print("Testing Simulation %d, Entropy 0.%d, Visual Range %d, Predator %d, Depth %d, Trial #%d"
              %(args[6], args[1][0], args[2], args[4][0], args[3], args[5]))
    Path((args[0])+'/Data').mkdir(parents=True, exist_ok=True)
    filename = args[0] + "/Data/Results_" + str(args[5]) + ".txt"
    print(filename)
    with open(filename, 'w') as f:
        f.write("Hello world!")

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

tags = enum('READY', 'DONE', 'EXIT', 'START')


if __name__ == "__main__":
    shortest_paths = json.load(open("shortest_paths.json"))
    sys.setrecursionlimit(10000)
    rank = 0
    #comm = MPI.COMM_WORLD
    #size = comm.size
    #rank = comm.rank
    #status = MPI.Status()

    if rank == 0:
        with open('init_vars.pkl', 'r') as f:
            occlusions, predators = pickle.load(f)
        planningDir = "/home/german/ugurcan/simulations"
        occlusionsMasterList = GetOcclusions(planningDir)
        predatorLocationsMasterList = GetPredatorLocations(planningDir)
        with open('init_e.pkl', 'w') as f:
            pickle.dump([occlusions, predators], f)

        print("Starting simulation...")
    #     mainDir = os.path.dirname(os.getcwd())
    #     planningDir = os.getcwd()
    #
    #     #UnitTests()
    #
    #     if not os.path.exists('arguments.pkl'):
        depthList = [0]
        visualRange = [100]
    #         with open('variables.pkl', 'r') as f:
    #             _, predatorLocationsMasterList, occlusionsMasterList = pickle.load(f)
    #         #predatorLocationsMasterList = GetPredatorLocations(mainDir)
    #         #occlusionsMasterList = GetOcclusions(mainDir)
    #
    #         #Get only mid entropy environments
    #         midEntropyOcclusionList = [(ent_ind, val) for sim_sublist in occlusionsMasterList
    #                                 for ent_ind, val in enumerate(sim_sublist) if ent_ind in range(4, 7)]
    #         midEntropyPredatorLocations = [(val_ind, val) for sim_sublist in predatorLocationsMasterList
    #                                        for ent_ind, ent_sublist in enumerate(sim_sublist) for val_ind, val in enumerate(ent_sublist)
    #                                        if ent_ind in range(4, 7)]
        arguments = []
        simulationIndex = -1
        for s, simulations in enumerate(occlusionsMasterList):
            for e, occlusionList in enumerate(simulations):
                for pl in predatorLocationsMasterList[s][e]:
                    for trial in range(ExperimentParams.MaxDoubles):
                        arguments.append([s, e, occlusionList, pl, trial, shortest_paths[s][e]])

        print(len(arguments))

        # with open('arguments.pkl', 'w') as f:
        #     pickle.dump(arguments, f)
        #     print('Pickled arguments for parallel processing...')
        #
        # with open('arguments.pkl', 'r') as f:
        #     #try:
        #     tasks = pickle.load(f)
        #     #except UnicodeDecodeError:  # python 3.x
        #     	#seek(0); tasks = pickle.load(f, encoding='latin1')
        # print('Loaded pickled arguments for parallel processing')
        # subsetTasks = [task for task in tasks]
        # subsetTasks = [(planningDir,) + task for task in subsetTasks]
        # nThread = 18
        # print("Starting parallel pool with {0} threads".format(nThread))
        for t in arguments:
            MultiExperiment(t)
        # with Pool(processes=nThread) as pool:
        #    pool.starmap(SafeMultiExperiment, subsetTasks)
	# #subsetTasks = subsetTasks[18000:]
    #     subsetTasks2 = [st for st in subsetTasks if st[3] == 100]
        task_index = 0
        numWorkers = nThread
        closedWorkers = 0
        print("Master starting with %d workers" % numWorkers)
        print("Total number of tasks %d" % len(subsetTasks))
	# #
    #     while closedWorkers < numWorkers:
    #         #data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
    #         #source = status.Get_source()
    #         #tag = status.Get_tag()
    #
    #         if tag == tags.READY:
    #             if task_index < len(subsetTasks2):
    #                 currentTask = subsetTasks2[task_index]
    #                 print(" Starting Simulation %d, Entropy 0.%d, Visual Range %d, Predator %d, Depth %d, Trial #%d"
    #                         %(currentTask[6], currentTask[1][0], currentTask[2], currentTask[4][0], currentTask[3], currentTask[5]))
    #                 print("Sending task %d:%d to worker %d" % (task_index, len(subsetTasks2), source))
    #                 comm.send(currentTask, dest=source, tag=tags.START)
    #                 task_index += 1
    #             else:
    #                 comm.send(None, dest=source, tag=tags.EXIT)
    #
    #         elif tag == tags.DONE:
    #             print("Finished processing worker %d" % source)
    #
    #         elif tag == tags.EXIT:
    #             print("Worker %d exited." % source)
    #             closedWorkers += 1
    #
    #     print("Master finishing...")
    #     sys.exit(1)
    #
    # else:
    #     name = MPI.Get_processor_name()
    #     print("I am a worker with rank %d on %s." % (rank, name))
    #
    #     while True:
    #         comm.send(None, dest=0, tag=tags.READY)
    #         task = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
    #         tag = status.Get_tag()
    #
    #         if tag == tags.START:
    #             SafeMultiExperiment(task)
    #             #MPITest(task)
    #             comm.send(None, dest=0, tag=tags.DONE)
    #
    #         elif tag == tags.EXIT:
    #             break
    #
    #     comm.send(None, dest=0, tag=tags.EXIT)
