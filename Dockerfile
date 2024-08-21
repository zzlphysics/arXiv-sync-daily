# Use an official Python runtime as the base image
FROM python:3.9.19
# Set the working directory in the container to /app
WORKDIR /app

# Create Downloads directory
RUN mkdir /app/Downloads && mkdir /app/log

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY ./arxiv_download.py .

# Install cron
RUN apt-get update && apt-get -y install cron

# Add crontab file in the cron directory
COPY my-cron /etc/cron.d/my-cron

# RUN echo "0 6 * * 1-5 python /app/arxiv_download.py >> /app/log/cron.log 2>&1" | tee  -a /etc/cron.d/my-cron

# Give execution rights on the cron job
RUN chmod 0755 /etc/cron.d/my-cron

# Apply cron job
RUN crontab /etc/cron.d/my-cron

# Create the log file to be able to run tail
RUN touch /app/log/cron.log

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Run the entrypoint script on container startup
ENTRYPOINT ["/entrypoint.sh"]

# Run the command on container startup
# RUN python arxiv_download.py >> /app/log/cron.log 2>&1
CMD []
