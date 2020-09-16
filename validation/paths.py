import resources
import map


Astar = "astar"
Euclidean = "euclidean"
Manhattan = "manhattan"


class Paths:
    def __init__(self, world, path_type):
        paths_json = resources.get_resource("paths", world.name, path_type)

        self.moves = paths_json["moves"]
        self.steps = paths_json["steps"]
        self.map = map.Map(world)

    def get_move(self, coordinates1, coordinates2):
        cell1 = self.map.cell(coordinates1)
        cell2 = self.map.cell(coordinates2)
        index = cell1["id"] * len(self.map.world.cells) + cell2["id"]
        return self.moves[index], self.steps[index]

