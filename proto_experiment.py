from backend.simulation.parsers.world_parser import WorldParser

def main():
    #! prototype experiment to print world information
    world_filename = "experiments/worlds/world_test1.json"
    world = WorldParser.Parse(world_filename)
    print(world)
    
if __name__ == "__main__":
    main()