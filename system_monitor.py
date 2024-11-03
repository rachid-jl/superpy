# system_monitor.py

import psutil
import subprocess
from datetime import datetime
from loguru import logger
from rich.console import Console, Theme
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich import box
from rich.live import Live
import time
import sys
import threading
import yaml
import os
import platform
import keyboard  # For non-blocking key detection

# Attempt to import log_parser, handle if not found
try:
    import log_parser  # Ensure this module exists
except ImportError:
    logger.error("log_parser module not found. Please ensure it is available.")
    sys.exit(1)

# Load configuration from config.yaml
CONFIG_FILE = 'config.yaml'

if not os.path.exists(CONFIG_FILE):
    logger.error(f"Configuration file '{CONFIG_FILE}' not found.")
    sys.exit(1)

with open(CONFIG_FILE, 'r') as f:
    try:
        config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing configuration file: {e}")
        sys.exit(1)

# Extract configurations
MONITORED_SERVICES = config.get('services', ['ssh.service', 'cron.service', 'networking.service'])
LOG_LIMIT = config.get('log_limit', 10)
REFRESH_RATE = config.get('refresh_rate', 2)  # in seconds

# Configure Loguru to log errors and above to a file with rotation
logger.remove()  # Remove default handlers
logger.add("system_monitor.log", level="ERROR", rotation="500 KB", retention="10 days", compression="zip")

# Define themes from configuration
themes_config = config.get('themes', {})
light_theme = Theme(themes_config.get('light', {}))
dark_theme = Theme(themes_config.get('dark', {}))

# Initialize console with dark theme by default
console = Console(theme=dark_theme)

# Lock for thread-safe theme switching
theme_lock = threading.Lock()
current_theme = "dark"

def get_system_metrics():
    """
    Collects and returns system metrics like CPU, memory, disk, and network usage.
    """
    try:
        metrics = {
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory": psutil.virtual_memory()._asdict(),
            "disk": psutil.disk_usage('/')._asdict(),
            "network": psutil.net_io_counters()._asdict()
        }
        return metrics
    except Exception as e:
        logger.exception("Failed to collect system metrics")
        return {}

def get_pmu_services():
    """
    Retrieves a list of specific services to monitor.
    """
    return MONITORED_SERVICES

def get_service_status(service_name):
    """
    Retrieves the status of a given service.
    """
    if platform.system() != "Linux":
        logger.warning("Service monitoring is only supported on Linux systems.")
        return {
            "name": service_name,
            "status": "Unsupported",
            "enabled": "Unsupported",
            "active_state": "Unsupported",
            "sub_state": "Unsupported",
        }

    try:
        result = subprocess.run(['systemctl', 'is-active', service_name], capture_output=True, text=True, timeout=5)
        status = result.stdout.strip()
        active = status == "active"
        
        result_enabled = subprocess.run(['systemctl', 'is-enabled', service_name], capture_output=True, text=True, timeout=5)
        enabled = result_enabled.stdout.strip()
        
        return {
            "name": service_name,
            "status": "Running" if active else "Not Running",
            "enabled": enabled.capitalize(),
            "active_state": status.capitalize(),
            "sub_state": "N/A",  # systemctl is-active doesn't provide sub-state directly
        }
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout while checking status for service: {service_name}")
    except Exception as e:
        logger.exception(f"Error retrieving status for service: {service_name}")

    return {
        "name": service_name,
        "status": "Unknown",
        "enabled": "Unknown",
        "active_state": "Unknown",
        "sub_state": "Unknown",
    }

def generate_system_report(log_limit=10):
    """
    Generates a report with system metrics, service statuses, and error logs.
    """
    pmu_services = get_pmu_services()
    report = {
        "timestamp": datetime.now(),
        "system_metrics": get_system_metrics(),
        "services_status": [get_service_status(service) for service in pmu_services],
        "kernel_logs": log_parser.get_kernel_logs(limit=log_limit),
        "middleware_logs": log_parser.get_middleware_logs(limit=log_limit),
        "system_logs": log_parser.get_system_logs(limit=log_limit)
    }
    return report

def create_dashboard(report):
    """
    Creates and returns the dashboard layout with updated data.
    """
    with theme_lock:
        # Create a layout with three rows
        layout = Layout()

        # Split the layout into header, body, and footer
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=1),
        )

        # Header with timestamp
        header_text = f"System Monitor - Last Updated: {report['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"
        layout["header"].update(Panel(header_text, style="header"))

        # Body - split into upper and lower sections
        layout["body"].split_column(
            Layout(name="upper", ratio=2),
            Layout(name="lower", ratio=1),
        )

        # Upper layout split into two columns
        layout["body"]["upper"].split_row(
            Layout(name="metrics"),
            Layout(name="services"),
        )

        # Lower layout split into three columns for logs
        layout["body"]["lower"].split_row(
            Layout(name="kernel_logs"),
            Layout(name="middleware_logs"),
            Layout(name="system_logs"),
        )

        # System Metrics
        metrics_table = Table(title="System Metrics", style="info", box=box.SQUARE)
        metrics_table.add_column("Metric", style="bold green")
        metrics_table.add_column("Value", style="bold cyan")

        cpu_usage = report['system_metrics']['cpu_usage']
        cpu_usage_str = f"{cpu_usage}%"
        if cpu_usage > 80:
            cpu_usage_str = f"[error]{cpu_usage}%[/error]"
        metrics_table.add_row("CPU Usage", cpu_usage_str)

        mem = report['system_metrics']['memory']
        mem_used_gb = round((mem['total'] - mem['available']) / (1024 ** 3), 2)
        mem_total_gb = round(mem['total'] / (1024 ** 3), 2)
        mem_percent = mem['percent']
        mem_usage_str = f"{mem_used_gb} GB / {mem_total_gb} GB ({mem_percent}%)"
        if mem_percent > 80:
            mem_usage_str = f"[error]{mem_usage_str}[/error]"
        metrics_table.add_row("Memory Used", mem_usage_str)

        disk = report['system_metrics']['disk']
        disk_used_gb = round(disk['used'] / (1024 ** 3), 2)
        disk_total_gb = round(disk['total'] / (1024 ** 3), 2)
        disk_percent = disk['percent']
        disk_usage_str = f"{disk_used_gb} GB / {disk_total_gb} GB ({disk_percent}%)"
        if disk_percent > 80:
            disk_usage_str = f"[error]{disk_usage_str}[/error]"
        metrics_table.add_row("Disk Used", disk_usage_str)

        net = report['system_metrics']['network']
        net_sent_mb = round(net['bytes_sent'] / (1024 ** 2), 2)
        net_recv_mb = round(net['bytes_recv'] / (1024 ** 2), 2)
        metrics_table.add_row("Network Sent", f"{net_sent_mb} MB")
        metrics_table.add_row("Network Received", f"{net_recv_mb} MB")

        # Services Status
        services_table = Table(title="Services Status", style="info", box=box.SQUARE)
        services_table.add_column("Service", style="bold green")
        services_table.add_column("Status", style="bold cyan")
        services_table.add_column("Enabled", style="bold cyan")
        services_table.add_column("Active State", style="bold cyan")
        services_table.add_column("Sub State", style="bold cyan")
        services_table.add_column("Problem", style="bold red")

        services_status = report.get("services_status", [])
        if services_status:
            for service in services_status:
                service_name = service.get("name", "Unknown")
                status = service.get("status", "Unknown")
                enabled = service.get("enabled", "Unknown")
                active_state = service.get("active_state", "Unknown")
                sub_state = service.get("sub_state", "Unknown")
                problem = "[bold green]No[/bold green]" if status == "Running" else "[error]Yes[/error]"
                services_table.add_row(
                    service_name,
                    status,
                    enabled,
                    active_state,
                    sub_state,
                    problem
                )
        else:
            services_table.add_row("No services found.", "", "", "", "", "")

        layout["body"]["upper"]["metrics"].update(metrics_table)
        layout["body"]["upper"]["services"].update(services_table)

        # Kernel Logs
        kernel_logs = report.get("kernel_logs", [])
        if kernel_logs:
            kernel_logs_table = Table(title="Kernel Error Logs", style="info", box=box.SQUARE, show_lines=True)
            kernel_logs_table.add_column("Timestamp", style="dim", width=20)
            kernel_logs_table.add_column("Message", style="bold", overflow="fold", max_width=60)
            for log in kernel_logs:
                timestamp = log.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
                message = log.get('message', 'No message')
                kernel_logs_table.add_row(timestamp, message)
            layout["body"]["lower"]["kernel_logs"].update(kernel_logs_table)
        else:
            layout["body"]["lower"]["kernel_logs"].update(Panel("[bold yellow]No kernel error logs found.[/bold yellow]", title="Kernel Error Logs"))

        # Middleware Logs
        middleware_logs = report.get("middleware_logs", {})
        if any(middleware_logs.values()):
            middleware_logs_table = Table(title="Middleware Error Logs", style="info", box=box.SQUARE, show_lines=True)
            middleware_logs_table.add_column("Log File", style="dim")
            middleware_logs_table.add_column("Message", style="bold", overflow="fold", max_width=60)
            for log_file, logs_list in middleware_logs.items():
                for line in logs_list:
                    middleware_logs_table.add_row(log_file, line)
            layout["body"]["lower"]["middleware_logs"].update(middleware_logs_table)
        else:
            layout["body"]["lower"]["middleware_logs"].update(Panel("[bold yellow]No middleware error logs found.[/bold yellow]", title="Middleware Error Logs"))

        # System Logs
        system_logs = report.get("system_logs", [])
        if system_logs:
            system_logs_table = Table(title="System Error Logs", style="info", box=box.SQUARE, show_lines=True)
            system_logs_table.add_column("Timestamp", style="dim", width=20)
            system_logs_table.add_column("Message", style="bold", overflow="fold", max_width=60)
            for log in system_logs:
                timestamp = log.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
                message = log.get('message', 'No message')
                system_logs_table.add_row(timestamp, message)
            layout["body"]["lower"]["system_logs"].update(system_logs_table)
        else:
            layout["body"]["lower"]["system_logs"].update(Panel("[bold yellow]No system error logs found.[/bold yellow]", title="System Error Logs"))

        # Footer with instructions
        footer_text = "Press 'd' to toggle dark/light mode | Press 'Ctrl+C' to exit"
        layout["footer"].update(Panel(footer_text, style="footer"))

    return layout

def handle_input():
    """
    Handles non-blocking user input to toggle themes.
    """
    global current_theme
    try:
        while True:
            if keyboard.is_pressed('d'):
                with theme_lock:
                    if current_theme == "dark":
                        console.theme = light_theme
                        current_theme = "light"
                        logger.info("Switched to Light Theme")
                    else:
                        console.theme = dark_theme
                        current_theme = "dark"
                        logger.info("Switched to Dark Theme")
                # Debounce to prevent rapid toggling
                time.sleep(0.5)
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass  # Allow graceful exit

def validate_services(services):
    """
    Validates if the services exist on the system.
    """
    if platform.system() != "Linux":
        logger.warning("Service validation is only supported on Linux systems.")
        return

    for service in services:
        try:
            subprocess.run(['systemctl', 'status', service], capture_output=True, text=True, timeout=5)
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout while validating service: {service}")
        except Exception as e:
            logger.exception(f"Error validating service: {service}")

def main():
    # Validate services before starting
    validate_services(MONITORED_SERVICES)

    # Start a separate thread to handle key input
    input_thread = threading.Thread(target=handle_input, daemon=True)
    input_thread.start()

    try:
        with Live(console=console, screen=True, auto_refresh=False) as live:
            while True:
                report = generate_system_report(log_limit=LOG_LIMIT)
                dashboard = create_dashboard(report)
                live.update(dashboard, refresh=True)
                time.sleep(REFRESH_RATE)
    except KeyboardInterrupt:
        console.clear()
        print("Exiting dashboard.")
    except Exception as e:
        logger.exception("An unexpected error occurred.")
        console.clear()
        print("An unexpected error occurred. Check the log file for details.")

if __name__ == "__main__":
    if platform.system() != "Linux":
        print("Warning: This script is primarily designed for Linux systems.")
    main()
