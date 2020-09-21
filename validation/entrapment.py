from paths import Paths

class Entrapment:
    def __init__(self, paths):
        for source in paths.map.world.cells:
            for destination in paths.map.world.cells:
                move = paths.get_move()
