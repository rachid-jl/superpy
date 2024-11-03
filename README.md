
# SuperPy

SuperPy is a versatile system monitoring tool that provides both a web-based dashboard and a console-based monitor. It allows users to track system metrics, services, and logs with customizable themes and settings.

## Installation

### Create a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Offline Installation

If your environment has restricted internet access, follow these steps:

### Clone the Repository

```bash
git clone https://github.com/rachid-jl/superpy.git
cd superpy
```

### Create a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies from offline_packages

```bash
pip install --no-index --find-links=offline_packages -r requirements.txt
```

#### Explanation:

- `--no-index`: Prevents pip from accessing the internet.
- `--find-links=offline_packages`: Tells pip to look for packages in the offline_packages directory.

## Configuration

SuperPy uses a `config.yaml` file to manage its settings. Below is an overview of the configuration options:

```yaml
# config.yaml

services:
  - ssh.service
  - cron.service
  - networking.service

log_limit: 50
refresh_rate: 10  # in seconds

themes:
  light:
    info: "black on white"
    warning: "yellow"
    error: "bold red"
    header: "bold black on white"
    footer: "bold black on white"
  dark:
    info: "white on black"
    warning: "yellow"
    error: "bold red"
    header: "bold white on blue"
    footer: "bold white on blue"
```

### Configuration Options

- **services**: List of systemd services to monitor.
- **log_limit**: Number of recent log entries to display.
- **refresh_rate**: Interval (in seconds) at which the dashboard refreshes.
- **themes**: Defines color schemes for light and dark modes in the console monitor.

## Customizing `config.yaml`

### Add or Remove Services

```yaml
services:
  - nginx.service
  - mysql.service
  - ssh.service
```

### Adjust Log and Refresh Settings

```yaml
log_limit: 100
refresh_rate: 5  # Update every 5 seconds
```

### Customize Themes

```yaml
themes:
  light:
    info: "blue on white"
    warning: "orange"
    error: "bold red"
    header: "bold white on green"
    footer: "bold white on green"
  dark:
    info: "cyan on black"
    warning: "magenta"
    error: "bold red"
    header: "bold white on darkblue"
    footer: "bold white on darkblue"
```

## Usage

### Web Dashboard

1. **Activate the Virtual Environment**:

    ```bash
    source venv/bin/activate
    ```

2. **Run the Dashboard**:

    ```bash
    python system_dashboard.py
    ```

3. **Access the Dashboard**: Open [http://127.0.0.1:8050/](http://127.0.0.1:8050/) in your browser.

### Console Monitor

1. **Activate the Virtual Environment**:

    ```bash
    source venv/bin/activate
    ```

2. **Run the Console Monitor**:

    ```bash
    python system_monitor.py
    ```

3. **Using the Console Monitor**:
    - **Theme Toggling**: Press the `d` key to switch between light and dark themes.
    - **Exit**: Press `Ctrl+C` to exit.

## Project Structure

```
superpy/
├── README.md
├── config.yaml
├── log_parser.py
├── offline_packages/
│   ├── cysystemd-1.6.2.tar.gz
│   ├── loguru-0.7.2-py3-none-any.whl
│   └── ...
├── requirements.txt
├── system_dashboard.py
└── system_monitor.py
```

### Key Files

- **README.md**: Project documentation.
- **config.yaml**: Configuration file for system monitoring settings.
- **log_parser.py**: Module for parsing system logs.
- **offline_packages/**: Pre-downloaded packages for offline installation.
- **requirements.txt**: Lists project dependencies.
- **system_dashboard.py**: Web-based dashboard.
- **system_monitor.py**: Console-based monitor.

## Troubleshooting

1. **Missing Dependencies**:
   Ensure all dependencies are installed:

   ```bash
   pip install -r requirements.txt
   ```

2. **Permission Issues**:
   If running `system_monitor.py` requires root privileges, use `sudo`:

   ```bash
   sudo python system_monitor.py
   ```

3. **Service Not Found**:
   Verify the services in `config.yaml` exist on your system.

4. **Web Dashboard Not Accessible**:
   Check if port 8050 is blocked or try accessing via your machine’s IP address.

5. **Log Parsing Errors**:
   Ensure `journalctl` is installed and accessible.

## Contributing

1. **Fork the Repository**.
2. **Clone Your Fork**:

    ```bash
    git clone https://github.com/your-username/superpy.git
    cd superpy
    ```

3. **Create a New Branch**:

    ```bash
    git checkout -b feature/your-feature-name
    ```

4. **Make Your Changes**.
5. **Commit and Push Your Changes**:

    ```bash
    git add .
    git commit -m "Add feature: description of your feature"
    git push origin feature/your-feature-name
    ```

6. **Create a Pull Request**.

## License

This project is licensed under the MIT License.

## Acknowledgments

- **Dash by Plotly**: Interactive web applications.
- **Rich**: Console output formatting.
- **Loguru**: Simplified logging.
- **psutil**: System information retrieval.