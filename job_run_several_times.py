import subprocess

def run_all_simulations(num_simulations=1):
    for i in range(num_simulations):
        print(f"Running simulation {i}")
        # Launch the run_several_times.py script with argument i
        result = subprocess.run(['python', 'run_several_times.py', str(i)])

        if result.returncode != 0:
            print(f"Simulation {i} encountered an error (code {result.returncode}). Stopping.")
            break


if __name__ == "__main__":
    run_all_simulations()
