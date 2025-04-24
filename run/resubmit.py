#!/usr/bin/env python3
import os
import sys
import subprocess
import re
import glob
import time

# GPU usage file
GPU_USAGE_FILE = os.path.expanduser("~/.openfe_gpu_usage")

def get_free_gpus():
    """Find available GPUs."""
    used_gpus = set()
    
    # Check GPU usage file
    if os.path.exists(GPU_USAGE_FILE):
        with open(GPU_USAGE_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    gpu_id = parts[0]
                    pid = parts[1]
                    # Check if process is still running
                    try:
                        if subprocess.run(['ps', '-p', pid], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0:
                            used_gpus.add(gpu_id)
                    except:
                        pass
    
    # Get all GPUs (assuming 8 GPUs, numbered 0-7)
    all_gpus = set(str(i) for i in range(8))
    free_gpus = list(all_gpus - used_gpus)
    
    return sorted(free_gpus)

def get_running_jobs():
    """Get list of currently running jobs."""
    running = []
    try:
        ps_output = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        for line in ps_output.stdout.splitlines():
            if 'openfe quickrun' in line:
                matches = re.findall(r'openfe quickrun\s+([^\s]+\.json|"[^"]+\.json"|\'[^\']+\.json\')', line)
                for match in matches:
                    job = match.strip('"\'')
                    if '_gpu' not in job:
                        running.append(os.path.basename(job))
    except Exception as e:
        print(f"Error getting running jobs: {e}")
    
    # Remove duplicates
    return list(set(running))

def is_job_completed(work_dir, job_base):
    """Check if a job is completed by looking for output JSON file."""
    output_pattern = os.path.join(work_dir, f"{job_base}_gpu*.json")
    return len(glob.glob(output_pattern)) > 0

def mark_gpu_used(gpu_id, pid, job_name):
    """Mark a GPU as being used in the GPU usage file."""
    try:
        with open(GPU_USAGE_FILE, 'a+') as f:
            # First seek to beginning and read to check if this GPU is already registered
            f.seek(0)
            lines = f.readlines()
            new_lines = []
            for line in lines:
                if not line.startswith(f"{gpu_id} "):
                    new_lines.append(line)
            
            # Rewrite file without this GPU's entry
            f.seek(0)
            f.truncate()
            for line in new_lines:
                f.write(line)
            
            # Add the new entry
            timestamp = int(time.time())
            f.write(f"{gpu_id} {pid} {timestamp} {job_name}\n")
    except Exception as e:
        print(f"Error updating GPU usage file: {e}")

def submit_job(job_file, gpu_id, work_dir):
    """Submit a job to a specific GPU."""
    # Get base filename and set up output names
    job_base = os.path.basename(job_file).replace('.json', '')
    output_file = f"{job_base}_gpu{gpu_id}.json"
    output_dir = f"{job_base}_gpu{gpu_id}"
    
    # Skip if already completed
    if is_job_completed(work_dir, job_base):
        print(f"Job {job_base} already completed, skipping")
        return False
    
    # Set up environment variables
    env = os.environ.copy()
    env['CUDA_VISIBLE_DEVICES'] = str(gpu_id)
    env['OPENMM_DEFAULT_PLATFORM'] = 'CUDA'
    
    # Use a proper subprocess with taskset to bind to specific cores
    cpu_range = f"{int(gpu_id)*8}-{int(gpu_id)*8+7}"
    
    # Build the command
    cmd = [
        'nohup',
        'taskset', '-c', cpu_range,
        'openfe', 'quickrun', job_file,
        '-o', output_file,
        '-d', output_dir
    ]
    
    print(f"Submitting {job_base} to GPU {gpu_id}")
    
    # Submit the job
    try:
        with open(f"{job_base}_gpu{gpu_id}.log", "w") as log_file:
            process = subprocess.Popen(
                cmd,
                stdout=log_file,
                stderr=log_file,
                cwd=work_dir,
                env=env,
                start_new_session=True  # This detaches the process
            )
        
        # Wait briefly to ensure process starts
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is None:
            # Process is still running
            mark_gpu_used(gpu_id, process.pid, job_base)
            print(f"Successfully started {job_base} on GPU {gpu_id} (PID: {process.pid})")
            return True
        else:
            print(f"Failed to start {job_base} on GPU {gpu_id}")
            return False
    
    except Exception as e:
        print(f"Error submitting job {job_base}: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python resubmit.py <work_directory>")
        sys.exit(1)
    
    work_dir = sys.argv[1]
    if not os.path.isdir(work_dir):
        print(f"Error: {work_dir} is not a directory")
        sys.exit(1)
    
    # Change to work directory
    os.chdir(work_dir)
    
    # First run check_completion.py to get status
    try:
        subprocess.run(['python3', 'check_completion.py'], check=True)
    except:
        print("Warning: Failed to run check_completion.py")
    
    # Get list of currently running jobs
    running_jobs = get_running_jobs()
    print(f"Currently running jobs: {len(running_jobs)}")
    for job in running_jobs:
        print(f"  {job}")
    
    # Get list of free GPUs
    free_gpus = get_free_gpus()
    print(f"Found {len(free_gpus)} truly available GPUs: {free_gpus}")
    
    if not free_gpus:
        print("No GPUs available! All GPUs are currently in use.")
        sys.exit(0)
    
    # Find all JSON files in the transformations directory
    transforms_dir = os.path.join(work_dir, "network_setup", "transformations", "transformations")
    job_files = []
    try:
        job_files = glob.glob(os.path.join(transforms_dir, "easy_rbfe_*.json"))
        job_files = [f for f in job_files if not re.search(r'_gpu\d+\.json$', f)]
    except Exception as e:
        print(f"Error finding job files: {e}")
    
    if not job_files:
        print("No job files found!")
        sys.exit(0)
    
    # Filter out completed and running jobs
    pending_jobs = []
    for job_file in job_files:
        job_base = os.path.basename(job_file).replace('.json', '')
        if job_base in running_jobs:
            print(f"Job {job_base} is already running, skipping")
            continue
        
        if is_job_completed(transforms_dir, job_base):
            print(f"Job {job_base} is already completed, skipping")
            continue
        
        pending_jobs.append(job_file)
    
    print(f"Found {len(pending_jobs)} pending jobs to submit")
    
    # Submit jobs to available GPUs
    for i, job_file in enumerate(pending_jobs):
        if i >= len(free_gpus):
            print("No more free GPUs available")
            break
        
        gpu_id = free_gpus[i]
        submit_job(job_file, gpu_id, transforms_dir)
        
        # Wait a bit between submissions to avoid race conditions
        time.sleep(5)
    
    print("Finished submitting jobs")

if __name__ == "__main__":
    main()


