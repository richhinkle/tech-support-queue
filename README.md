# Tech Support Queue Simulation

This project simulates a tech support call center using discrete-event simulation with SimPy. It models customer arrivals, agent service, queueing, priority customers, and abandonment due to impatience.

## Features
- Simulates normal and priority customer calls
- Models agent availability and queueing
- Tracks wait times, service times, abandonments, and agent utilization
- Includes multiple scenarios (normal, high traffic, understaffed)
- **NEW:** Command line arguments for custom simulation runs
- **NEW:** Optional charting of queue length over time
- **NEW:** Save queue length chart to a PNG file

## Requirements
Install dependencies with:
```bash
pip install -r requirements.txt
```

## Usage
Run the simulation script from the command line:
```bash
python tech_support_sim.py
```

By default, the script will run three scenarios:
1. **Normal Operations**
2. **High Traffic Period**
3. **Understaffed**

Each scenario prints statistics and metrics to the console.

### Custom Simulation with Command Line Arguments
You can run a single custom scenario by providing any of the following arguments:
- `--sim_duration` (int): Simulation duration in minutes (default: 480)
- `--num_agents` (int): Number of support agents (default: 5)
- `--arrival_rate` (float): Customer arrival rate (customers per minute, default: 0.8)
- `--avg_call_duration` (float): Average call duration in minutes (default: 8)
- `--plot`: Show a chart of queue length over time after the simulation
- `--save_plot <filename.png>`: Save the queue length chart to a PNG file

#### Example: Custom Run with Plot
```bash
python tech_support_sim.py --sim_duration 300 --num_agents 4 --arrival_rate 1.0 --avg_call_duration 7 --plot
```

#### Example: Save Chart to File
```bash
python tech_support_sim.py --sim_duration 300 --num_agents 4 --arrival_rate 1.0 --avg_call_duration 7 --save_plot my_queue_chart.png
```

#### Example: Show and Save Chart
```bash
python tech_support_sim.py --sim_duration 300 --num_agents 4 --arrival_rate 1.0 --avg_call_duration 7 --plot --save_plot my_queue_chart.png
```

If any simulation parameter is provided, only a single scenario will run with those parameters. The `--plot` flag will display a matplotlib chart of the queue length over time, and the `--save_plot` flag will save it to a file. You can use either or both flags.

## Output
The script prints:
- Customer arrivals and departures
- Queue and agent status
- Summary statistics after each scenario
- (Optional) A chart of queue length over time if `--plot` is used
- (Optional) Saves the chart to a PNG file if `--save_plot` is used

## Extending the Script
You can further customize the simulation or add new features by editing `tech_support_sim.py`.

---

For questions or improvements, feel free to modify the code or open an issue! 