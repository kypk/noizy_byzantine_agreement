# Byzantine Agreement Protocol in a Small Quantum Network

## Description
This repository was created for the purposes of the [Research Project](https://github.com/TU-Delft-CSE/Research-Project) (2025) for [TU Delft](https://github.com/TU-Delft-CSE). It contains the code used to simulate a three-node quantum-aided weak broadcast protocol under the influence of measurement errors. For more details, see the [research paper](research_paper.pdf)

## Installation
1. Follow the [official instructions](https://squidasm.readthedocs.io/en/latest/installation.html) to install SquidASM. It is recommended to install SquidASM in a [virtual environment](https://docs.python.org/3/library/venv.html).

2. Clone this repository

3. (Optional) In order to generate graphs using the Python scripts provided here, you need to install matplotlib:
```
pip install matplotlib
```

## Usage
To run the simulation, activate the virtual environment (if you're using one) and navigate to the WBC folder:
```
source /path_to_venv/bin/activate
cd WBC
```

The simulation can then be run using Python:
```
python3 run_simulation.py
```

The following command-line arguments can be used:
- `--faulty`:    Specifies which node will be faulty. Possible values: "s", "r0". Any other value is considered No Faulty (Default: None)
- `-m`:      Specifies the range of m values to be simulated. Format: "m_from,m_to" (Default: "20,400")
- `--mu`:    Specifies the protocol's mu parameter (Default: 0.272)
- `-l`:      Specifies the protocol's lambda parameter (Default: 0.94)

The output is a table of m values and their respective failure probabilities in CSV format. Example:
```
20,0.52
30,0.48
40,0.35
50,0.31
60,0.37
70,0.44
80,0.27
90,0.16
100,0.27
...
```

## File structure
- `WBC/application.py`: Contains the protocol implementation
- `WBC/run_simulation.py`: Contains the simulation setup
- `WBC/config_nv.yaml`: Contains the NV device configuration in YAML format
- `WBC/config_general.yaml`: Contains a generic device configuration with no noise in YAML format
- `scatter.py`: Python script used to generate a graph from a single simulation
- `scatter_triple.py`: Python script used to generate a single graph with data from three simulations

## Support
For any questions regarding the implementation details, please contact me at [k.kyparos@gmail.com](mailto:k.kyparos@gmail.com)
