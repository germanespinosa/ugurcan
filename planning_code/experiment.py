from mcts import MCTS, SearchParams
from episode import Episode
from timeit import default_timer as timer
from statistics import STATISTICS

import csv, os# pickle, os
#, pathlib
#from pathlib2 import Path
#import cPickle as pickle
import pandas as pd

class Results:
    def __init__(self):
        self.Time = STATISTICS(0., 0.)
        self.Reward = STATISTICS(0., 0.)
        self.DiscountedReturn = STATISTICS(0., 0.)
        self.UndiscountedReturn = STATISTICS(0., 0.)
        self.Steps = STATISTICS(0., 0.)

    def Clear(self):
        self.Time.Clear()
        self.Reward.Clear()
        self.DiscountedReturn.Clear()
        self.UndiscountedReturn.Clear()
        self.Steps.Clear()


class ExperimentParams:
    SpawnArea = 4
    NumRuns = 20
    NumSteps = 200
    SimSteps = 1000
    TimeOut = 36000
    MinDoubles = 0
    MaxDoubles = 50
    NumDepth = 14
    NumPredatorLocations = 1000
    TransformDoubles = -1
    TransformAttempts = 1000
    Accuracy = 0.01
    UndiscountedHorizon = 100
    AutoExploration = True
    EntropyLevels = [float(i)/10. for i in range(0, 10)]


class Experiment:
    def __init__(self, real, simulator):
        self.Real = real
        self.Simulator = simulator
        self.Episode = Episode()

        if ExperimentParams.AutoExploration:
            if SearchParams.UseRave:
                SearchParams.ExplorationConstant = 0
            else:
                SearchParams.ExplorationConstant = self.Simulator.GetRewardRange()

        self.Results = Results()
        MCTS.InitFastUCB(SearchParams.ExplorationConstant)

    def Run(self, episodePickle):
        notOutOfParticles = True
        undiscountedReturn = 0.0
        discountedReturn = 0.0
        discount = 1.0

        state = self.Real.CreateStartState()
        currentState = self.Real.Copy(state)
        self.Episode.Add(-1, -1, currentState, 0)

        self.MCTS = MCTS(self.Simulator)

        start = timer()
        t = 0
        observation = 0
        self.NumObservation = 0

        if Path(episodePickle).is_file() and os.path.getsize(episodePickle) > 0:
            try:
                print("found pickled episode")
                with open(episodePickle, "rb") as f:
                    mcts, episode, exstate, t = pickle.load(f)
                    print("found pickled episode at t:%d"%t)
                    self.MCTS = mcts
                    self.Episode = episode
                    currentState = self.Real.Copy(exstate)
                    state = self.Real.Copy(exstate)
            except:
                print("pickled filed doesn't work, starting the run over...")
                pass

        while t < ExperimentParams.NumSteps:
            action = self.MCTS.SelectAction(state)

            terminal, state, observation, reward = self.Real.Step(state, action)
            currentState = self.Real.Copy(state)

            self.NumObservation += 1*(observation > 0)
            self.Results.Reward.Add(reward)
            undiscountedReturn += reward
            discountedReturn += reward * discount
            discount *= self.Real.GetDiscount()

            if SearchParams.Verbose:
                self.Real.DisplayState(state)

            if terminal:
                self.Episode.Add(action, observation, currentState, reward)
                self.Episode.Complete()
                break

            notOutOfParticles, beliefState = self.MCTS.Update(action, observation, reward)
            if not notOutOfParticles:
                print("random action selection")
                self.Episode.Add(action, observation, currentState, reward)
                break

#            if (timer() - start) > ExperimentParams.TimeOut:
#                break

            if t%2 == 0:
                with open(episodePickle, "wb") as f:
                    pickle.dump([self.MCTS, self.Episode, state, t], f)
                    print('pickled %s'%episodePickle)
        t += 1

        if not notOutOfParticles:
            if SearchParams.Verbose:
                print("Out of particles, finishing episode with SelectRandom")
            history = self.MCTS.GetHistory()

            while t <= ExperimentParams.NumSteps:
                t += 1

                action = self.Simulator.SelectRandom(state, history, self.MCTS.GetStatus())
                terminal, state, observation, reward = self.Real.Step(state, action)

                self.Results.Reward.Add(reward)
                undiscountedReturn += reward
                discountedReturn += reward * discount
                discount *= self.Real.GetDiscount()

                if SearchParams.Verbose:
                    self.Real.DisplayState(state)

                if terminal:
                    self.Episode.Add(action, observation, state, reward)
                    self.Episode.Complete()
                    break

                self.MCTS.History.Add(action, observation)
                self.Episode.Add(action, observation, state, reward)

    def DiscountedReturn(self, occlusions, visualRange, predatorHome, depth, knowledge,
                                    occlusionInd, predatorInd, trial, simulationDirectory):

        directory = simulationDirectory +'/VisualRange_%d/Predator_%d/Depth_%d'%(visualRange, predatorInd, depth)
        episodeFile = directory+'/Episode_%d.csv'%(trial)
        episodePickle = directory+'Episode_%d.pkl'%(trial)
        if Path(episodeFile).is_file():
            episode = pd.read_csv(episodeFile, header=0)
            if episode['Reward'].iloc[-1] !=  -1:
                return 1
            #print(episodeFile+' exists')
	    #if Path(episodePickle).is_file():
	#    try:    
	#        os.remove(episodePickle)
        #    except OSError:
        #        pass
	#    return 1
	#episodePickle = directory+'/Episode_%d.pkl'%(trial)
        Path(directory).mkdir(parents=True, exist_ok=True)

        #occlusionDirectory = simulationDirectory+'/Occlusion_%d'%(occlusionInd)
        occlusionFile = simulationDirectory+'/OcclusionCoordinates.csv'
        if not Path(occlusionFile).is_file():
            self.OcclusionCoords2CSV(occlusions, occlusionFile)

        self.Results.Clear()

        SearchParams.NumSimulations = depth
        SearchParams.NumStartState = depth
        SearchParams.Softmax = False
        if depth > 10:
            SearchParams.Softmax = True

        if int(depth * (10 ** ExperimentParams.TransformDoubles)) > 0:
            SearchParams.NumTransforms = int(depth * (10 ** ExperimentParams.TransformDoubles))
        else:
            SearchParams.NumTransforms = 1

        SearchParams.Softmax = False
        SearchParams.MaxAttempts = SearchParams.NumTransforms * ExperimentParams.TransformAttempts

        if visualRange <= 3:
            SearchParams.MaxDepth = 50
        elif visualRange == 4:
            SearchParams.MaxDepth = 100
        elif visualRange > 4:
            SearchParams.MaxDepth = 200

        self.Real.__init__(self.Real.XSize, self.Real.YSize, visualrange=visualRange, occlusions=occlusions)
        self.Real.PredatorHome = predatorHome
        self.Real.SetKnowledge(knowledge)

        self.Simulator.__init__(self.Simulator.XSize, self.Simulator.YSize, visualrange=visualRange, occlusions=occlusions)
        self.Simulator.PredatorHome = predatorHome
        self.Simulator.SetKnowledge(knowledge)

        #if SearchParams.Verbose:
        #    self.Real.InitializeDisplay()

        self.Run(episodePickle)
        self.Episode.Episode2CSV(episodeFile)
        self.Episode.Clear()

        return 1

    def Dictionary2CSV(self, dictTable, filename):
        columns = sorted(dictTable)
        with open(filename, 'w') as f:
            writer = csv.writer(f); writer.writerow(columns); writer.writerows(zip(*[dictTable[col] for col in columns]))

    def OcclusionCoords2CSV(self, occlusions, occlusionFile):
        occlusionDict = {}
        occlusionDict['X'] = []; occlusionDict['Y'] = []
        for coord in occlusions:
            occlusionDict['X'].append(coord.X); occlusionDict['Y'].append(coord.Y)

        self.Dictionary2CSV(occlusionDict, occlusionFile)
