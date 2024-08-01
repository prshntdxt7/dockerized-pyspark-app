import subprocess
import os

def run_command(command):
    print(f"Running command: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Error:", result.stderr)
    return result

def build_image():
    command = "docker build -t visual-content-case-study ."
    result = run_command(command)
    if result.returncode == 0:
        print("Docker image built successfully.")
    else:
        print("Failed to build Docker image.")
        exit(1)

def run_container():
    project_path = os.path.abspath(".")
    print(f"project_path:{project_path}")
    command = "docker run -p 8888:8888 -v C:/Users/prdixit/Downloads/visual-content-case-study-main/visual-content-case-study-main:/visual-content-case-study-main  visual-content-case-study"
    result = run_command(command)
    if result.returncode == 0:
        print("Docker container started successfully.")
    else:
        print("Failed to start Docker container.")
        exit(1)

def main():
    build_image()
    run_container()

if __name__ == "__main__":
    main()
