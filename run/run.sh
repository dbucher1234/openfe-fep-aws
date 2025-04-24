#!/bin/bash
# run.sh - Submit jobs only on GPUs that are truly free using a centralized GPU usage file.

# Global GPU usage file and lock file locations
GPU_USAGE_FILE="$HOME/.openfe_gpu_usage"
LOCK_FILE="$GPU_USAGE_FILE.lock"

# Initialize the GPU usage file if it doesn't exist.
[ -f "$GPU_USAGE_FILE" ] || touch "$GPU_USAGE_FILE"

# Function to update the global GPU usage file with a new record.
update_gpu_usage() {
    local gpu_id=$1
    local pid=$2
    local job_name=$3
    local timestamp
    timestamp=$(date +%s)
    (
      flock -x 200
      # Remove any old record for this GPU.
      grep -v "^$gpu_id " "$GPU_USAGE_FILE" > "${GPU_USAGE_FILE}.tmp"
      echo "$gpu_id $pid $timestamp $job_name" >> "${GPU_USAGE_FILE}.tmp"
      mv "${GPU_USAGE_FILE}.tmp" "$GPU_USAGE_FILE"
    ) 200>"$LOCK_FILE"
}

# Function to check if a GPU is free.
# A GPU is considered free if no record exists OR the record is stale (older than 60 seconds and PID is dead).
is_gpu_free() {
    local gpu_id=$1
    local now
    now=$(date +%s)
    local record
    record=$(grep "^$gpu_id " "$GPU_USAGE_FILE")
    if [ -z "$record" ]; then
        return 0  # No record; GPU is free.
    fi
    local pid timestamp diff
    pid=$(echo "$record" | awk '{print $2}')
    timestamp=$(echo "$record" | awk '{print $3}')
    diff=$(( now - timestamp ))
    if [ $diff -gt 60 ]; then
        if ! ps -p "$pid" > /dev/null 2>&1; then
            # Stale record; remove it.
            (
              flock -x 200
              sed -i "/^$gpu_id /d" "$GPU_USAGE_FILE"
            ) 200>"$LOCK_FILE"
            return 0
        fi
    fi
    return 1  # GPU is in use.
}

# Function to clean up stale records in the global GPU usage file.
cleanup_gpu_usage() {
    local now
    now=$(date +%s)
    (
      flock -x 200
      cp "$GPU_USAGE_FILE" "${GPU_USAGE_FILE}.tmp"
      > "$GPU_USAGE_FILE"
      while IFS= read -r line; do
          local gpu_id pid timestamp job_name diff
          gpu_id=$(echo "$line" | awk '{print $1}')
          pid=$(echo "$line" | awk '{print $2}')
          timestamp=$(echo "$line" | awk '{print $3}')
          job_name=$(echo "$line" | awk '{print $4}')
          diff=$(( now - timestamp ))
          if [ $diff -gt 60 ] && ! ps -p "$pid" > /dev/null 2>&1; then
              echo "Cleaning up stale record for GPU $gpu_id, job $job_name (PID: $pid)" >> "$PWD/network_setup/transformations/transformations/openfe_run.log"
          else
              echo "$line" >> "$GPU_USAGE_FILE"
          fi
      done < "${GPU_USAGE_FILE}.tmp"
      rm -f "${GPU_USAGE_FILE}.tmp"
    ) 200>"$LOCK_FILE"
}

# Function to get pending jobs from the work directory.
get_pending_jobs() {
    local work_dir="$PWD/network_setup/transformations/transformations"
    local pending=()
    for file in "$work_dir"/easy_rbfe_*.json; do
        # Skip if the filename contains _gpu (i.e. it's an output file)
        if [[ "$file" != *"_gpu"*".json" ]]; then
            local base
            base=$(basename "$file" .json)
            # If no output directory exists for this job, then it's pending.
            if ! find "$work_dir" -maxdepth 1 -type d -name "${base}_gpu*" | grep -q .; then
                pending+=("$file")
            fi
        fi
    done
    echo "${pending[@]}"
}

# Function to submit a job to a specific GPU.
submit_job() {
    local gpu_id=$1
    local job_file=$2
    local work_dir="$PWD/network_setup/transformations/transformations"
    local base
    base=$(basename "$job_file" .json)
    local timeout="24h"
    if [[ "$job_file" == *"solvent"* ]]; then
        timeout="6h"
    fi
    local cpu_start=$((gpu_id * 24))
    local cpu_end=$((cpu_start + 23))
    echo "Submitting $job_file on GPU $gpu_id" >> "$work_dir/openfe_run.log"
    
    (
        cd "$work_dir" || exit 1
        export CUDA_VISIBLE_DEVICES=$gpu_id
        export OPENMM_DEFAULT_PLATFORM=CUDA
        timeout $timeout taskset -c $cpu_start-$cpu_end \
            openfe quickrun "$base.json" \
            -o "${base}_gpu${gpu_id}.json" \
            -d "${base}_gpu${gpu_id}" >> openfe_run.log 2>> openfe_run_error.log
        exit_code=$?
        if [ $exit_code -eq 0 ]; then
            echo "Job $base.json completed on GPU $gpu_id" >> openfe_run.log
        else
            echo "Job $base.json failed on GPU $gpu_id (exit code $exit_code)" >> openfe_run_error.log
        fi
    ) &
    local pid=$!
    update_gpu_usage "$gpu_id" "$pid" "$base.json"
    sleep 2
}

# Main loop.
work_dir="$PWD/network_setup/transformations/transformations"
mkdir -p "$work_dir/gpu_locks"
touch "$work_dir/running_jobs.pid"

while true; do
    # Clean up stale GPU usage records.
    cleanup_gpu_usage

    # Retrieve pending jobs.
    pending_jobs=($(get_pending_jobs))
    if [ ${#pending_jobs[@]} -eq 0 ]; then
        echo "No pending jobs found" >> "$work_dir/openfe_run.log"
        sleep 60
        continue
    fi

    # Loop through GPU IDs 0-7.
    for gpu_id in {0..7}; do
        if is_gpu_free "$gpu_id"; then
            if [ ${#pending_jobs[@]} -gt 0 ]; then
                job_file="${pending_jobs[0]}"
                # Remove the submitted job from the pending array.
                pending_jobs=("${pending_jobs[@]:1}")
                submit_job "$gpu_id" "$job_file"
            fi
        fi
    done
    sleep 60
done

