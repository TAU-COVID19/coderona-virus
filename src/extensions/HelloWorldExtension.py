from src.simulation.simulation import Simulation
class HelloWorldExtension(Simulation):
    def __init__(self,parent: Simulation):
        print("In printing Ctor")

    def DoProcessing(self):
        print("Hello World")