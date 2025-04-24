#!/usr/bin/env python
import os
import glob
import subprocess
import re
from datetime import timedelta

def print_gpu_usage():
    """Print the GPU usage summary from ../.openfe_gpu_usage."""
    gpu_usage_file = os.path.join(os.getcwd(), "..", ".openfe_gpu_usage")
    if os.path.exists(gpu_usage_file):
        try:
            with open(gpu_usage_file, "r") as f:
                print("=== GPU Usage Summary ===")
                print(f.read().strip())
                print()
        except Exception as e:
            print(f"Error reading GPU usage file: {e}")
    else:
        print("GPU usage summary file not found.\n")

def get_running_jobs(work_dir):
    """Get dictionary of running job filenames in the specified directory (and its subdirectories) using regex."""
    running_jobs = {}
    try:
        ps_output = subprocess.run(['ps', 'aux'], capture_output=True, text=True).stdout
        # Regex to capture job filename ending in .json that appears after "openfe quickrun" and before " -o"
        pattern = re.compile(r"openfe\s+quickrun\s+(.+?\.json)\s+-o")
        for line in ps_output.splitlines():
            if "openfe quickrun" in line:
                match = pattern.search(line)
                if match:
                    job_name = match.group(1).strip()
                    # Filter to include only jobs that reside in work_dir (or its subdirectories)
                    job_glob = os.path.join(work_dir, "**", job_name)
                    if glob.glob(job_glob, recursive=True):
                        running_jobs[job_name] = None
    except Exception as e:
        print(f"Error in get_running_jobs: {e}")
    return running_jobs

def is_job_completed(work_dir, job_base):
    """
    Check if a job has completed by looking for output files.
    A job is only considered complete if it has a corresponding output JSON file with non-zero size.
    Just having a directory is not enough to indicate completion.
    """
    # The output pattern should match files like job_base_gpuX.json
    output_pattern = os.path.join(work_dir, f"{job_base}_gpu*.json")
    output_files = glob.glob(output_pattern)
    
    for output_file in output_files:
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            return True
    
    # If we reach here, no valid output file was found
    return False

def get_compounds(sdf_file="ligands.sdf"):
    """Count unique compounds from ligands.sdf file."""
    compounds = set()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sdf_path = os.path.join(script_dir, sdf_file)
    
    try:
        with open(sdf_path, 'r') as f:
            current_compound = None
            for line in f:
                line = line.strip()
                if line == "$$$$":
                    current_compound = None
                    continue
                # The first non-empty, non-'RDKit' line is taken as the compound name.
                if current_compound is None and line and not line.startswith("RDKit"):
                    compounds.add(line)
                    current_compound = line
        
        if compounds:
            print(f"Found {len(compounds)} compounds in {sdf_path}: {sorted(compounds)}")
        else:
            print(f"Warning: No compound names found in {sdf_path}")
        return compounds
        
    except FileNotFoundError:
        print(f"Warning: {sdf_path} not found. Cannot determine exact compound count.")
        return None
    except Exception as e:
        print(f"Error reading SDF file: {e}")
        return None

def estimate_remaining_time(remaining_complex, remaining_solvent, running_complex, running_solvent):
    """Estimate time to completion in hours."""
    # New jobs: 8h for complex, 0.5h for solvent
    new_time = len(remaining_complex) * 8 + len(remaining_solvent) * 0.5
    
    # Running jobs: 4h for complex, 0.25h for solvent (assuming roughly halfway done)
    running_time = len(running_complex) * 4 + len(running_solvent) * 0.25
    
    return new_time + running_time

def main():
    # Print GPU usage summary (all running jobs on the instance)
    print_gpu_usage()
    
    # Define the work directory relative to the current working directory
    work_dir = os.path.join(os.getcwd(), "network_setup", "transformations", "transformations")
    
    # Gather all input JSON files (excluding GPU output files) from work_dir (and its subdirectories)
    all_jobs = []
    for root, dirs, files in os.walk(work_dir):
        for file in files:
            if file.startswith("easy_rbfe_") and file.endswith(".json") and '_gpu' not in file:
                rel_path = os.path.relpath(os.path.join(root, file), work_dir)
                all_jobs.append(rel_path)
    
    # Get compounds from ligands.sdf (assumed to be in the same directory as this script)
    compounds = get_compounds()
    if compounds is None:
        # Fallback: extract compound names from transformation filenames.
        compounds = set()
        for job in all_jobs:
            parts = job.split('_')
            for i, part in enumerate(parts):
                if part in ['complex', 'solvent'] and i > 2:
                    compounds.add('_'.join(parts[2:i]))
    
    # Separate the jobs into complex and solvent jobs
    complex_jobs = [j for j in all_jobs if 'complex' in j]
    solvent_jobs = [j for j in all_jobs if 'solvent' in j]
    
    # Get running jobs using the filtering that only looks within work_dir.
    running_jobs = get_running_jobs(work_dir)
    running_complex = [j for j in running_jobs if 'complex' in j]
    running_solvent = [j for j in running_jobs if 'solvent' in j]
    
    # Mark a job as completed if it is not currently running and an output file or directory exists.
    completed_jobs = []
    for job in all_jobs:
        if job not in running_jobs:
            job_base = os.path.splitext(job)[0]
            if is_job_completed(work_dir, job_base):
                completed_jobs.append(job)
    
    # Determine jobs that remain (not completed and not currently running)
    remaining_complex = [j for j in complex_jobs if j not in completed_jobs and j not in running_jobs]
    remaining_solvent = [j for j in solvent_jobs if j not in completed_jobs and j not in running_jobs]
    
    # Calculate time estimates.
    total_hours = estimate_remaining_time(
        remaining_complex, remaining_solvent,
        running_complex, running_solvent
    )
    
    # Number of active GPUs (jobs currently running)
    active_gpus = len(running_jobs)
    parallel_time = total_hours / max(active_gpus, 1)  # Avoid division by zero
    
    # Print the status report.
    print("=== OpenFE Job Status Report ===")
    print(f"Total compounds: {len(compounds)}")
    print(f"Total transformations: {len(all_jobs)}")
    print(f"Completed: {len(completed_jobs)}")
    print(f"Currently running: {len(running_jobs)}")
    print(f"Remaining to start: {len(remaining_complex) + len(remaining_solvent)}\n")
    
    print("Pending jobs breakdown:")
    print(f"  Complex transformations: {len(remaining_complex)}")
    print(f"  Solvent transformations: {len(remaining_solvent)}\n")
    
    print("Time estimates for remaining jobs:")
    print(f"  Single GPU: {timedelta(hours=total_hours)}")
    print(f"  Parallel ({active_gpus} active GPUs): {timedelta(hours=parallel_time)}\n")
    
    if running_jobs:
        print("Currently running jobs:")
        for job in running_jobs:
            print(f"  - {job}")
        print()
    
    if remaining_complex:
        print("Pending complex transformations:")
        for job in remaining_complex:
            print(f"  - {job}")
        print()
    
    if remaining_solvent:
        print("Pending solvent transformations:")
        for job in remaining_solvent:
            print(f"  - {job}")
        print()
    
    if completed_jobs:
        print("Completed jobs:")
        for job in completed_jobs:
            print(f"  - {job}")

if __name__ == "__main__":
    main()
