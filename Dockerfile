FROM apache/airflow:2.5.1

USER root

# Install SSH server
RUN apt-get update && \
    apt-get install -y openssh-server && \
    mkdir -p /var/run/sshd

# Set root password
RUN echo 'root:airflow' | chpasswd

# Configure SSH
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/UsePAM yes/UsePAM no/' /etc/ssh/sshd_config

# Set default directory on SSH login
RUN echo 'cd /opt/airflow' >> /root/.bashrc

# Expose SSH port
EXPOSE 22

# Switch back to airflow user
USER ${AIRFLOW_UID:-50000}

# Default command (overridden in docker-compose.yml)
# CMD ["bash", "-c", "service ssh start"]
