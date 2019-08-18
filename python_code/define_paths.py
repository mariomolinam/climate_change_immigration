# DEFINE PATHS depending on hostname server
hostname = socket.gethostname()
if hostname == 'molina':
    path_data = "/home/mario/Documents/environment_data/mmp_data"
    path_git = "/home/mario/mm2535@cornell.edu/projects/ra_filiz/climate_change_immigration"
    # sys.path.insert(0, path_git) # local
elif hostname == 'sdl3':
    path_git = "/home/mm2535/documents/climate_change_immigration"
    path_data = "/home/mm2535/data/climate_change"
    # sys.path.insert(0, path_git) # sdl3
elif hostname == 'sdl1':
    path_git = "/home/mm2535/documents/climate_change_immigration"
    path_data = "/home/mm2535/documents/data/climate_change"        # sdl1
