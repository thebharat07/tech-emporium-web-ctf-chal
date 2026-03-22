# 1. Use a stable lightweight Python environment
FROM python:3.11-slim

# 2. Install system dependencies (GCC for SUID binary, libpq for PostgreSQL)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Create a low-privilege user (The web app runs as this user)
RUN useradd -m ctf-user

# 4. Set up the application directory
WORKDIR /app

# 5. Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Set up the ROOT FLAG (Hidden from low-privilege users)
RUN mkdir -p /root && chown root:root /root && chmod 700 /root

# 7. Compile the SUID Binary (The "Maintenance Tool" exploit)
# We copy the C code, compile it, set the SUID bit, then DELETE the source.
COPY sys-check.c /tmp/sys-check.c
RUN gcc /tmp/sys-check.c -o /usr/bin/sys-check \
    && chown root:root /usr/bin/sys-check \
    && chmod 4755 /usr/bin/sys-check \
    && rm /tmp/sys-check.c

# 8. Copy the Web Application source code
COPY . .

# 9. PROTECT THE SOURCE CODE (Permission Lockdown)
# We make root the owner of everything in /app. 
# This makes app.py, templates, etc. READ-ONLY for the ctf-user.
RUN chown -R root:root /app && chmod -R 755 /app

# 10. SETUP THE UPLOADS FOLDER (The only writable area)
# The ctf-user needs ownership here to save the 2 allowed files.
RUN mkdir -p /app/uploads \
    && chown -R ctf-user:ctf-user /app/uploads \
    && chmod 733 /app/uploads 
    # 733 = User can Write/Exec, but others can't easily list files.

# 11. CLEAN UP THE EVIDENCE
# Remove the Dockerfile and requirements so players don't get the "Answer Key".
RUN rm Dockerfile requirements.txt

# 12. RUN AS THE LOW-PRIVILEGE USER
USER ctf-user

# Expose the Flask port
EXPOSE 5000

# Start the application
CMD ["python", "app.py"]