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
    return trajectories[-1][0]["x"] == 0 and trajectories[-1][0]["y"] == -7


def equal(c0, c1):
    return c0["x"] == c1["x"] and c0["y"] == c1["y"]


def add(c0, c1):
    return {"x": c0["x"] + c1["x"], "y": c0["y"] + c1["y"]}


def detect_backward(p_trajectories, p_visibility, p_paths):
    for location_index in range(1, len(p_trajectories) - 1):
        if p_visibility.is_visible(p_trajectories[location_index][1], p_trajectories[location_index][0]):
            if equal(p_trajectories[location_index - 1][1], p_trajectories[location_index + 1][1]):
                move = p_paths.get_move(p_trajectories[location_index][1], p_trajectories[location_index][0])[0]
                if not equal( add(p_trajectories[location_index][1], move),  p_trajectories[location_index + 1][1]):
                    return True
    return False


def count_records(l, entropy):
    counter = 0
    for r in l:
        if entropy == r[0]:
            counter += 1
    return counter

def detect_entrapment(p_trajectories, p_paths):
    for location_index in range(1, len(p_trajectories) - 1):
        move, steps = p_paths.get_move(p_trajectories[location_index][1], p_trajectories[location_index][0])
        if steps == -1:
            return True
    return False

def compute_distance(c0,c1):
    return ((c0["x"] - c1["x"]) ** 2 + (c0["y"] - c1["y"]) ** 2) ** .5

def detect_missing_belief_state(p_trajectories,p_visibility, p_paths):
    last_view = 0
    distance = 100
    for location_index in range(1, len(p_trajectories) - 1):
        if p_visibility.is_visible(p_trajectories[location_index][1], p_trajectories[location_index][0]):
            distance = compute_distance(p_trajectories[location_index][1], p_trajectories[location_index][0])
            last_view = location_index

    if last_view<len(p_trajectories) - 5:
        last_distance = compute_distance(p_trajectories[-1][1], p_trajectories[-1][0])
        if (last_distance>=distance):
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
total = 0
total_e = [0 for x in range(10)]
total_ed = [0 for x in range(10)]
win_e = [0 for x in range(10)]
win_ed = [0 for x in range(10)]
for e in range(10):
    for s in range(20):
        occlusions = load_occlusions(simulation=s, entropy=e)
        world_name = "world_%d_%d" % (s, e)
        world = World(world_name)
        paths = Paths(world, "euclidean")
        visibility = Visibility(world)
        for p in range(5):
            for i in range(50):
                failed = False
                total_e[e] += 1
                total += 1
                record = [e, s, p, i]
                filename = get_path(simulation=s, entropy=e, predator_location=p, episode=i)
                if not os.path.isfile(filename):
                    failed = True
                    missing.append(record)
                    continue

                trajectories = load_trajectories(filename)
                is_win = get_winner(trajectories)
                if is_win:
                    win_e[e] += 1
                predator_location = trajectories[0][1]
                if i == 0:
                    first_predator_location = predator_location
                if first_predator_location != predator_location:
                    failed = True
                    inconsistent.append(record)
                if visibility.map.cell(predator_location)["occluded"] == 1:
                    failed = True
                    isolated.append(record)
                    continue
                if detect_entrapment(trajectories, paths):
                    failed = True
                    entrapment.append(record)
                if detect_backward(trajectories, visibility, paths):
                    failed = True
                    backward_random.append(record)
                if detect_missing_belief_state(trajectories,visibility,paths):
                    failed = True
                    belief_state.append(record)
                if not failed and is_win:
                    win_ed[e] += 1
                total_ed[e] += 1
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
        print(
            "\r Processed %d : missing %d (%.2f%%) belief state %d (%.2f%%) disconnected %d (%.2f%%) location %d (%.2f%%) entrapment %d (%.2f%%) backward %d (%.2f%%)       " % (
            total, len(missing), len(missing) / total * 100, len(belief_state), len(belief_state) / total * 100, len(isolated), len(isolated) / total * 100, len(inconsistent),
            len(inconsistent) / total * 100, len(entrapment), len(entrapment) / total * 100, len(backward_random),
            len(backward_random) / total * 100), end="")
print()
print("Failed episodes: %d" % failed_episodes)

for e in range(10):
    print("- entropy %d: missing %d (%.2f%%) belief state %d (%.2f%%) disconnected %d (%.2f%%) location %d (%.2f%%) entrapment %d (%.2f%%) backward %d (%.2f%%)       " % (
            e, count_records(missing, e), count_records(missing, e) / total_e[e] * 100, count_records(belief_state, e), count_records(belief_state, e) / total_e[e] * 100, count_records(isolated, e), count_records(isolated, e) / total_e[e] * 100, count_records(inconsistent,e),
            count_records(inconsistent, e) / total_e[e] * 100, count_records(entrapment, e), count_records(entrapment,e) / total_e[e] * 100, count_records(backward_random, e),
            count_records(backward_random, e) / total_e[e] * 100))

print ("adjusted results:")
for e in range(10):
    print("- entropy %d: old survival rate: %.2f%% adjusted %.2f%%" % (e, win_e[e] / total_e[e] * 100,  win_ed[e] / total_ed[e] * 100))

problems = {"backward_random": backward_random, "entrapment": entrapment, "isolated": isolated, "belief_state": belief_state,"inconsistent": inconsistent, "missing": missing }

save_json(problems, "results/problems.json")