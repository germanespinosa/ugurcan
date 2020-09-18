from map import Map
from world import World
from paths import Paths
from visibility import Visibility
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
    episode = {"world": "world_%d_%d" % (simulation, entropy), "goal": {"x": 0, "y": -7}, "trajectories": [], "values": [], "winner": 0}
    for agents_coordinates in p_trajectories:
        episode["trajectories"].append([{"x": coordinate["x"] - 7, "y": -(coordinate["y"] - 7)} for coordinate in agents_coordinates])
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
            p_trajectories.append([{"y": -int(values[2]) + 7, "x": int(values[1]) - 7}, {"y": -int(values[5]) + 7, "x": int(values[4]) - 7}])
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


def get_winner(p_trajectories):
    return trajectories[-1][0]["x"] == 7 and trajectories[-1][0]["y"] == 14


def detect_entrapment(p_trajectories, m):
    counters = [0 for x in range(len(world.cells))]
    for locations in p_trajectories:
        index = m.cell(locations[1])["id"]
        counters[index] += 1
    for counter in counters:
        if counter > 3:
            return True
    return False


def detect_backward(p_trajectories, visibility):
    for location_index in range(1, len(p_trajectories) - 1):
        if visibility.is_visible(p_trajectories[location_index][1], p_trajectories[location_index][0]):
            if equal(p_trajectories[location_index - 1][1],p_trajectories[location_index + 1][1]):
                return True
    return False


def equal(c0,c1):
    return  c0["x"] == c1["x"] and c0["y"] == c1["y"]


def detect_backward(p_trajectories, visibility):
    for location_index in range(1, len(p_trajectories) - 1):
        if visibility.is_visible(p_trajectories[location_index][1], p_trajectories[location_index][0]):
            if equal(p_trajectories[location_index - 1][1],p_trajectories[location_index + 1][1]):
                return True
    return False


failed_episodes = 0
failures_per_entropy = [0 for x in range(10)]

backward_random = []
entrapment = []
isolated = []
belief_state = []
inconsistent = []
missing = []
for e in range(10):
    for s in range(20):
        occlusions = load_occlusions(simulation=s, entropy=e)
        world_name = "world_%d_%d" % (s, e)
        world = World(world_name)
        paths = Paths(world, "euclidean")
        visibility = Visibility(world)
        print("\r Entropy %d, Simulation %d : missing %d disconnected %d inconsistent %d entrapment %d  random backward %d        " % (e, s, len(missing), len(isolated), len(inconsistent), len(entrapment), len(backward_random)), end="")
        for p in range(5):
            for i in range(50):
                record = (e, s, p, i)
                filename = get_path(simulation=s, entropy=e, predator_location=p, episode=i)
                if not os.path.isfile(filename):
                    missing.append(record)
                    continue

                trajectories = load_trajectories(filename)
                predator_location = trajectories[0][1]
                if i == 0:
                    first_predator_location = predator_location
                if first_predator_location != predator_location:
                    inconsistent.append(record)
                if visibility.map.cell(predator_location)["occluded"] == 1:
                    isolated.append(record)
                    continue
                if detect_entrapment(trajectories, visibility.map):
                    entrapment.append(record)
                if detect_backward(trajectories,visibility):
                    backward_random.append(record)
                    # if moves_backward(trajectories, visibility):
                    #     backward_random.append(record)
                    #
                    # heatmap = create_heatmap(trajectories)
                    # winner = get_winner(trajectories)
                    # if ()
                    # if winner and count_repetitions(heatmap, 6) > 0:
                    #     failed_episodes += 1
                    #     failures_per_entropy[e] += 1
                    #     print("https://germanespinosa.github.io/cellworld_www/episode_replay.html?experiment=0&group=%d&world=%d&configuration=%d&episode=%d&step=0&&agent=0" % (e, s, p, i))
                    #     # print("fail")
                    #     # fig, (ax1, ax2) = plt.subplots(1, 2)
                    #     # im = ax1.imshow(heatmap, cmap='Reds')
                    #     # im = ax2.imshow(create_heatmap(trajectories, 0), cmap='Blues')
                    #     # ax1.add_patch(Rectangle((trajectories[0][1]["y"] - .5, trajectories[0][1]["x"] - .5), 1, 1, fill=False,
                    #     #                         edgecolor='green', lw=3))
                    #     # ax2.add_patch(Rectangle((trajectories[0][0]["y"] - .5, trajectories[0][0]["x"] - .5), 1, 1, fill=False,
                    #     #                         edgecolor='green', lw=3))
                    #     #
                    #     # for occlusion in occlusions:
                    #     #     ax1.add_patch(
                    #     #         Rectangle((occlusion["x"] - .5, occlusion["y"] - .5), 1, 1, fill=True, facecolor='black', lw=1))
                    #     #     ax2.add_patch(
                    #     #         Rectangle((occlusion["x"] - .5, occlusion["y"] - .5), 1, 1, fill=True, facecolor='black', lw=1))
                    #     # plot_filename = filename.replace(".csv", ".png")
                    # # plt.savefig(plot_filename)
                    # # plt.show();
                    # save_json(get_episode(s, e, trajectories), "/home/german/simulation/cellworld_results/experiment_0/group_%d/world_%d/configuration_%d/episode_%d.json" %(e,s,p,i))
print()
print("Failed episodes: %d" % failed_episodes)

for e in range(10):
    print("- entropy %d: %d" % (e, failures_per_entropy[e]))
