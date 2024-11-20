import subprocess

def get_conda_envs():
    # Fetch a list of Conda environments
    try:
        result = subprocess.run(["conda", "env", "list"], stdout=subprocess.PIPE, text=True)
        envs = []
        for line in result.stdout.splitlines():
            if line.startswith("#") or not line.strip():
                continue
            env_name = line.split()[0]
            envs.append(env_name)
        return envs
    except Exception as e:
        print(f"Error fetching environments: {e}")
        return []