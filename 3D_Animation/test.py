from pathlib import PosixPath

# Your PosixPath object
path_object = PosixPath('/mnt/data0/sEEG_DATA/MCW-FH_006/EMU/EMU-015_subj-MCW-FH_006_task-gaps/EMU-015_subj-MCW-FH_006_task-gaps_run-35_RIP.nev')

# Use PosixPath object as a string
path_string = str(path_object)

# Alternatively, you can directly use the object in contexts that expect a string
# For example, you can print it directly
print(path_object)
