import psutil

# Get the number of free CPU cores
free_cores = psutil.cpu_count(logical=True)

# Get the amount of free memory in bytes
free_memory = psutil.virtual_memory().available

# Convert free memory to gigabytes (GB)
free_memory_gb = round(free_memory / (1024**3), 2)

# Print the number of free CPU cores and amount of free memory
print(f"Free CPU cores: {free_cores}")
print(f"Free memory: {free_memory_gb} GB")
