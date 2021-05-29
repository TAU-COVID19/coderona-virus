from src.simulation.simulation import Simulation
class EmptyExtension(Simulation):
    def __init__(self,parent: Simulation):
        pass

    def DoProcessing(self):
        pass