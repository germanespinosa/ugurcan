import numpy as np
import os.path
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import json


def load_json(file_name):
    with open(file_name) as f:
        return json.loads(f.read())


def save_json(value, file_name):
    folder = file_name.replace(file_name.split("/")[-1], "")
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(file_name, 'w') as outfile:
        json.dump(value, outfile)

def get_episode (simulation, entropy, p_trajectories):
    episode = {"world": "world_%d_%d" % (simulation, entropy), "goal": {"x": 0, "y": 7}, "trajectories": [], "values": [], "winner": 0}
    for agents_coordinates in p_trajectories:
        episode["trajectories"].append([[coordinate["x"]-7,coordinate["y"]-7] for coordinate in agents_coordinates])
        episode["values"].append([0 for coordinate in agents_coordinates])
    episode["winner"] = episode["trajectories"][-1][0] != [7,0]
    return episode

def get_path(simulation, entropy, predator_location=-1, episode=-1):
    path = "/home/german/ugurcan/Data_NatComm/Simulation_%d/Occlusion_%d/" % (simulation, entropy)
    if predator_location >= 0:
        path += "Predator_%d/" % predator_location
        if episode >= 0:
            path += "Depth_5000/Episode_%d.csv" % episode
    return path


def loaf_file(file_name):
    with open(file_name) as f:
        return f.readlines()


def load_trajectories(file_name):
    lines = loaf_file(file_name)
    p_trajectories = []
    for line in lines:
        values = line.split(',')
        if values[1].isnumeric():
            p_trajectories.append([{"y": int(values[2]), "x": int(values[1])}, {"y": int(values[5]), "x": int(values[4])}])
    return p_trajectories


def create_heatmap(p_trajectories, agent=1):
    counters = np.zeros((15, 15), np.integer)
    for positions in p_trajectories:
        counters[(positions[agent]["x"], positions[agent]["y"])] += 1
    return counters


def count_repetitions(counters, limit=3):
    return (heatmap >= limit).sum()


def load_occlusions(simulation, entropy):
    lines = loaf_file(get_path(simulation, entropy) + "/OcclusionCoordinates.csv")
    p_occlusions = []
    for line in lines:
        values = line.split(',')
        if values[0].isnumeric():
            position = {"x": int(values[0]), "y": int(values[1])}
            p_occlusions.append(position)
    return p_occlusions

def get_winner ( p_trajectories ):
    return trajectories[-1][0]["x"] == 7 and trajectories[-1][0]["y"] == 14;


failed_episodes = 0
failures_per_entropy = [0 for x in range(10)]

for e in range(10):
    for s in range(20):
        occlusions = load_occlusions(simulation=s, entropy=e)
        for p in range(5):
            for i in range(50):
                filename = get_path(simulation=s, entropy=e, predator_location=p, episode=i)
                if os.path.isfile(filename):
                    trajectories = load_trajectories(filename)
                    heatmap = create_heatmap(trajectories)
                    winner = get_winner(trajectories)
                    if winner == 0 and count_repetitions(heatmap, 3) > 0:
                        failed_episodes += 1
                        failures_per_entropy[e] += 1
                        # print("Simulation %d, Entropy %d, Predator location %d, Episode %d: " % (s, e, p, i), end="")
                        # print("fail")
                        # fig, (ax1, ax2) = plt.subplots(1, 2)
                        # im = ax1.imshow(heatmap, cmap='Reds')
                        # im = ax2.imshow(create_heatmap(trajectories, 0), cmap='Blues')
                        # ax1.add_patch(Rectangle((trajectories[0][1]["y"] - .5, trajectories[0][1]["x"] - .5), 1, 1, fill=False,
                        #                         edgecolor='green', lw=3))
                        # ax2.add_patch(Rectangle((trajectories[0][0]["y"] - .5, trajectories[0][0]["x"] - .5), 1, 1, fill=False,
                        #                         edgecolor='green', lw=3))
                        #
                        # for occlusion in occlusions:
                        #     ax1.add_patch(
                        #         Rectangle((occlusion["x"] - .5, occlusion["y"] - .5), 1, 1, fill=True, facecolor='black', lw=1))
                        #     ax2.add_patch(
                        #         Rectangle((occlusion["x"] - .5, occlusion["y"] - .5), 1, 1, fill=True, facecolor='black', lw=1))
                        # plot_filename = filename.replace(".csv", ".png")
                    # plt.savefig(plot_filename)
                    # plt.show();
                    save_json(get_episode(s, e, trajectories), "/home/german/simulation/cellworld_results/experiment_0/group_%d/world_%d/configuration_%d/episode_%d.json" %(e,s,p,i))


print("Failed episodes: %d" % failed_episodes)

for e in range(10):
    print("- entropy %d: %d" % (e, failures_per_entropy[e]))
