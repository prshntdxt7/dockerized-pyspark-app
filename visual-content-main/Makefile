# NOTE: chocolatey package installation is required to install makefile, which failed to install since this being the work machine.
# NOTE: alternate python utility to this makefile is available under src as: [run_build_and_run.py], which wraps the similar docker build and docker run commands to assist
# NOTE: in build and run processes

# Variables
IMAGE_NAME = visual-content-case-study
CONTAINER_NAME = visual-content-case-study-container
JUPYTER_PORT = 8888

# Build the Docker image
build:
	docker build -t $(IMAGE_NAME) .

# Run the Docker container
run:
	docker run -p 8888:8888 -v C:/Users/prdixit/Downloads/visual-content-case-study-main/visual-content-case-study-main:/visual-content-case-study-main  $(IMAGE_NAME)

# Stop the Docker container
stop:
	docker stop $(CONTAINER_NAME)

# Remove the Docker container
clean:
	docker rm $(CONTAINER_NAME)

# Rebuild and run the Docker container
rebuild: stop clean build run

# Execute the main Python script inside the container
exec:
	docker exec -it $(CONTAINER_NAME) python src/process_images.py --images data/images.jsonl --tags data/image_tags.jsonl --main_images data/main_images.jsonl --output_cdc output/output_cdc.jsonl --output_snapshot output/output_snapshot.jsonl --output_metrics output/output_metrics.jsonl
