import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def loaf_file(filename):
    with open(filename) as f:
        return f.readlines()


def load_trajectories(simulation, entropy, predator_location, episode):
    lines = loaf_file("/home/german/ugurcan/Data_NatComm/Simulation_%d/Occlusion_%d/Predator_%d/Depth_5000/Episode_%d.csv" % (simulation, entropy, predator_location, episode))
    p_trajectories = []
    for line in lines:
        values = line.split(',')
        if values[1].isnumeric():
            prey_coord = (int(values[2]), int(values[1]))
            predator_coord = (int(values[5]), int(values[4]))
            p_trajectories += [[prey_coord, predator_coord]]
    return p_trajectories


def create_heatmap(p_trajectories, agent=1):
    counters = np.zeros((15, 15), np.integer)
    for positions in p_trajectories:
        counters[positions[agent]] += 1
    return counters


def count_repetitions(counters, limit=3):
    return (heatmap >= limit).sum()


def load_occlusions(simulation, entropy):
    lines = loaf_file("/home/german/ugurcan/Data_NatComm/Simulation_%d/Occlusion_%d/OcclusionCoordinates.csv" % (simulation, entropy))
    p_occlusions = []
    for line in lines:
        values = line.split(',')
        if values[0].isnumeric():
            position = (int(values[0]), int(values[1]))
            p_occlusions += [position]
    return p_occlusions


for s in range(20):
    for e in range(10):
        occlusions = load_occlusions(simulation=s, entropy=e)
        for p in range(5):
            for i in range(50):
                trajectories = load_trajectories(simulation=s, entropy=e, predator_location=p, episode=i)
                heatmap = create_heatmap(trajectories)
                if trajectories[-1][0] == (14,7) and count_repetitions(heatmap, 6) > 0:
                    fig, (ax1, ax2) = plt.subplots(1,2)
                    im = ax1.imshow(heatmap, cmap='Reds')
                    im = ax2.imshow(create_heatmap(trajectories, 0), cmap='Blues')
                    ax1.add_patch(Rectangle((trajectories[0][1][1] - .5, trajectories[0][1][0] - .5), 1, 1, fill=False, edgecolor='green', lw=3))
                    ax2.add_patch(Rectangle((trajectories[0][0][1] - .5, trajectories[0][0][0] - .5), 1, 1, fill=False, edgecolor='green', lw=3))

                    for occlusion in occlusions:
                        ax1.add_patch(Rectangle((occlusion[0]-.5, occlusion[1]-.5), 1, 1, fill=True, facecolor='black', lw=1))
                        ax2.add_patch(Rectangle((occlusion[0]-.5, occlusion[1]-.5), 1, 1, fill=True, facecolor='black', lw=1))

                    plt.title("Simulation %d, Entropy %d, Predator location %d" % (s, e, p))
                    plt.show()

