# log_parser.py

import subprocess
from datetime import datetime
from loguru import logger

def get_kernel_logs(limit=10):
    """
    Retrieves the latest kernel error logs.
    """
    try:
        result = subprocess.run(['journalctl', '-k', '-p', 'err', '-n', str(limit)], capture_output=True, text=True, timeout=10)
        logs = []
        for line in result.stdout.strip().split('\n'):
            if line:
                # Example line format: "Sep 14 10:00:00 hostname kernel: Error message"
                parts = line.split(' ', 3)
                if len(parts) >= 4:
                    timestamp_str = ' '.join(parts[:3])
                    message = parts[3]
                    try:
                        timestamp = datetime.strptime(timestamp_str, '%b %d %H:%M:%S')
                        # As journalctl logs may not include the year, default to current year
                        timestamp = timestamp.replace(year=datetime.now().year)
                    except ValueError:
                        timestamp = datetime.now()
                    logs.append({"timestamp": timestamp, "message": message})
        return logs
    except subprocess.TimeoutExpired:
        logger.error("Timeout while retrieving kernel logs.")
    except Exception as e:
        logger.exception("Failed to retrieve kernel logs.")
    return []

def get_middleware_logs(limit=10):
    """
    Retrieves the latest middleware error logs.
    Customize this function based on where your middleware logs are stored.
    """
    # Example implementation: parse /var/log/middleware.log
    middleware_log_files = ['/var/log/middleware.log']  # Update with actual middleware log paths
    logs = {}
    for log_file in middleware_log_files:
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()[-limit:]
                logs[log_file] = [line.strip() for line in lines if 'error' in line.lower()]
        except FileNotFoundError:
            logger.warning(f"Middleware log file not found: {log_file}")
        except Exception as e:
            logger.exception(f"Failed to read middleware log file: {log_file}")
    return logs

def get_system_logs(limit=10):
    """
    Retrieves the latest system error logs.
    """
    try:
        result = subprocess.run(['journalctl', '-p', 'err', '-n', str(limit)], capture_output=True, text=True, timeout=10)
        logs = []
        for line in result.stdout.strip().split('\n'):
            if line:
                # Example line format: "Sep 14 10:00:00 hostname systemd: Error message"
                parts = line.split(' ', 3)
                if len(parts) >= 4:
                    timestamp_str = ' '.join(parts[:3])
                    message = parts[3]
                    try:
                        timestamp = datetime.strptime(timestamp_str, '%b %d %H:%M:%S')
                        # As journalctl logs may not include the year, default to current year
                        timestamp = timestamp.replace(year=datetime.now().year)
                    except ValueError:
                        timestamp = datetime.now()
                    logs.append({"timestamp": timestamp, "message": message})
        return logs
    except subprocess.TimeoutExpired:
        logger.error("Timeout while retrieving system logs.")
    except Exception as e:
        logger.exception("Failed to retrieve system logs.")
    return []
