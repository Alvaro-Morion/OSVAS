import os
import re
import numpy as np
import yaml
import pandas as pd

def main():
    # Default values defined in the notebook for Station and OSVAS install:
    OSVAS='/home/alvaro/master/TFM/OSVAS/'  # Main OSVAS path
    Station_name='Cabauw'

    # If an environment variable STATION or OSVAS exists, override the default
    Station_name = os.getenv("STATION_NAME", Station_name)
    OSVAS = os.getenv("OSVAS", OSVAS)

    print(f"Introducing soil initial condicions for: {Station_name} with OSVAS installation in {OSVAS}")

    # Extract Config file information

    CONFIG_PATH = os.path.join(OSVAS, "config_files", "Stations", f"{Station_name}.yml")

    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    station_info = config["Station_metadata"]
    patch = station_info["vegtype"]
    forcing_data = config["Forcing_data"]

    start_date = pd.to_datetime(forcing_data["run_start"])
    end_date = pd.to_datetime(forcing_data["run_end"])

    # Select PREP target and profile files

    TG_path = os.path.join(OSVAS, "profiles", Station_name,  f"TG_{start_date}.txt")
    WG_path = os.path.join(OSVAS, "profiles", Station_name,  f"WG_{start_date}.txt")

    target = './PREP.txt'

    try:
        TG = np.loadtxt(TG_path)
        WG = np.loadtxt(WG_path)
    except  IOError as e:
        print(e)
        return(1)

    pattern_TG = re.compile(rf"^&NATURE\s+TG(\d+)P{patch}$")
    pattern_WG = re.compile(rf"^&NATURE\s+WG(\d+)P{patch}$")

    with open(target, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):   
        line_stripped = line.strip()
        match = pattern_TG.match(line_stripped)
        if match:
            level = int(match.group(1)) - 1
            lines[i + 2] =  f"{TG[level]:.8E}\n"
            continue
        match = pattern_WG.match(line_stripped)
        if match:
            level = int(match.group(1)) - 1
            lines[i + 2] =  f"{WG[level]:.8E}\n"
            continue

    with open(target, "w") as f:
        f.writelines(lines)
    return(0)

if __name__ == "__main__":
    main()

