from src.simulation.simulation import Simulation
class HelloWorldExtension(Simulation):
    def __init__(self):
        print("In printing Ctor")

    def DoProcessing(self):
        print("Hello World")