# Name: s
# Dimensions: 2

# --- Set up executable path, do not edit ---
import sys
import inspect
#import numpy as np
this_file_loc = (inspect.stack()[0][1])
main_dir_loc = this_file_loc[:this_file_loc.index('ca_descriptions')]
sys.path.append(main_dir_loc)
sys.path.append(main_dir_loc + 'capyle')
sys.path.append(main_dir_loc + 'capyle/ca')
sys.path.append(main_dir_loc + 'capyle/guicomponents')
# ---

from capyle.ca import Grid2D, Neighbourhood, randomise2d
import capyle.utils as utils
import numpy as np
import random


def setup(args):
    """Set up the config object used to interact with the GUI"""
    config_path = args[0]
    config = utils.load(config_path)
    # -- THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED --
    config.title = "Fire spread CaA"
    config.dimensions = 2
    config.states = (0, 1, 2, 3, 4, 5,6)
    # STATES:
    # 0 Background
    # 1 Water
    # 2 Canyon
    # 3 Forest
    # 4 Village
    # 5 Fire
    # 6 Burnt out

	# config.num_generations = 100
    # -------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    config.state_colors = [(0.5,0.9,0.1),(0,0,1),(0.4,0.4,0.4), (0.4,0.6,0.37),(0,0,0), (1,0,0),(0.4,0,0)]
    config.grid_dims = (50,50)
    config.initial_grid = np.zeros(config.grid_dims)
    config.initial_grid[5:8,5:8] = 5
    config.initial_grid[10:15, 5:15] = 1
    config.initial_grid[5:35, 32:35] = 2
    config.initial_grid[30:41, 15:25] = 3
    config.initial_grid[48:50, :3] = 4
    config.wrap = False

	#set_grid_dims(dims = (200, 200))
    #set_initial_grid(grid)
	#config.inital_grid[1,1] = 1

    # ----------------------------------------------------------------------

    # the GUI calls this to pass the user defined config
    # into the main system with an extra argument
    # do not change
    if len(args) == 2:
        config.save()
        sys.exit()
    return config

def decision(probability):
    return random.random() < probability


def transition_function(grid, neighbourstates, neighbourcounts, decaygrid):
    """Function to apply the transition rules
    and return the new grid"""

    # Find cells in certain states
    cell_in_state_0 = (grid == 0)
    cell_in_state_2 = (grid == 2)
    cell_in_state_3 = (grid == 3)

    # Decay
    cell_in_state_5 = (grid == 5)

    # Find neighbours to these cells
    three_5_neighbours = (neighbourcounts[5] >= 3)
    one_5_neighbour = (neighbourcounts[5] >= 1)
    two_5_neighbours = (neighbourcounts[5] >= 2)
    four_5_neighbours = (neighbourcounts[5] >= 4)

    half_prob = decision(0.5)
    quarter_prob = decision(0.25)
    tenth_prob = decision(0.1)
    threequarter_prob = decision(0.75)
    ninetenth_prob = decision(0.9)

    # Make them Burn!!!
    zero_to_5 = (cell_in_state_0 & ((one_5_neighbour & tenth_prob) | (three_5_neighbours & half_prob) | (four_5_neighbours & threequarter_prob)))
    two_to_five = (cell_in_state_2 & ((one_5_neighbour & quarter_prob) | (two_5_neighbours & threequarter_prob)))
    three_to_five = (cell_in_state_3 & ((three_5_neighbours & tenth_prob) | (four_5_neighbours & quarter_prob)))


    # Minus one from burning cell count until it reaches 0
    decaygrid[cell_in_state_5] -= 1
    decayed_to_zero = (decaygrid == 0)

    grid[decayed_to_zero] = 6
    grid[zero_to_5 | two_to_five | three_to_five] = 5

    return grid


def main():
    """ Main function that sets up, runs and saves CA"""
    # Get the config object from set up
    config = setup(sys.argv[1:])

    decaygrid = np.zeros(config.grid_dims)

    decaygrid.fill(6)

    decaygrid[5:35, 32:35] = 5
    decaygrid[30:41, 15:25] = 50

    # Create grid object using parameters from config + transition function
    grid = Grid2D(config, (transition_function, decaygrid))

    # Run the CA, save grid state every generation to line
    timeline = grid.run()

    # Save updated config to file
    config.save()

    # Save timeline to file
    utils.save(timeline, config.timeline_path)

if __name__ == "__main__":

    main()
