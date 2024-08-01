FROM jupyter/pyspark-notebook:latest

# Set the working directory
WORKDIR /visual-content-case-study-main

# Copy the local project files to the container
COPY . /visual-content-case-study-main

# Install required packages
RUN pip install -r requirements.txt

# Jupyter Notebook default port
EXPOSE 8888

# Run Jupyter Notebook
CMD ["start-notebook.sh"]
