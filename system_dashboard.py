# system_dashboard.py

import dash
from dash import dcc, html
from dash.dependencies import Output, Input, State  # Ensure State is imported
import plotly.graph_objs as go
import psutil
import datetime

app = dash.Dash(__name__)
app.title = 'System Monitoring Dashboard'

# Define the layout with dcc.Store components for storing data
app.layout = html.Div(children=[
    html.H1('System Monitoring Dashboard', style={'textAlign': 'center'}),

    # Display live metrics
    html.Div(id='live-update-text', style={'textAlign': 'center'}),

    # Graphs for system metrics
    dcc.Graph(id='cpu-usage-graph'),
    dcc.Graph(id='memory-usage-graph'),
    dcc.Graph(id='disk-usage-graph'),
    dcc.Graph(id='network-io-graph'),

    # Hidden divs to store intermediate data
    dcc.Store(id='cpu-data-store', storage_type='memory'),
    dcc.Store(id='memory-data-store', storage_type='memory'),
    dcc.Store(id='disk-data-store', storage_type='memory'),
    dcc.Store(id='network-data-store', storage_type='memory'),

    # Interval component for updates
    dcc.Interval(
        id='interval-component',
        interval=2*1000,  # Update every 2 seconds
        n_intervals=0
    )
])

# Callback to update live metrics text
@app.callback(
    Output('live-update-text', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_metrics(n):
    metrics = get_system_metrics()
    style = {'padding': '5px', 'fontSize': '20px'}

    return [
        html.Span(f"CPU Usage: {metrics['cpu_percent']}%", style=style),
        html.Br(),
        html.Span(f"Memory Usage: {metrics['memory_percent']}%", style=style),
        html.Br(),
        html.Span(f"Disk Usage: {metrics['disk_percent']}%", style=style),
    ]

def get_system_metrics():
    """
    Collects and returns system metrics like CPU, memory, disk, and network usage.
    """
    metrics = {
        'cpu_percent': psutil.cpu_percent(interval=None),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'network_sent': psutil.net_io_counters().bytes_sent,
        'network_recv': psutil.net_io_counters().bytes_recv,
    }
    return metrics

# Callback to update CPU data store
@app.callback(
    Output('cpu-data-store', 'data'),
    Input('interval-component', 'n_intervals'),
    State('cpu-data-store', 'data')
)
def update_cpu_data(n, data):
    time_now = datetime.datetime.now().strftime('%H:%M:%S')
    cpu_percent = psutil.cpu_percent()

    if data is None:
        data = {'times': [], 'values': []}

    data['times'].append(time_now)
    data['values'].append(cpu_percent)

    # Keep only the last 50 entries
    data['times'] = data['times'][-50:]
    data['values'] = data['values'][-50:]

    return data

# Callback to update CPU graph
@app.callback(
    Output('cpu-usage-graph', 'figure'),
    Input('cpu-data-store', 'data')
)
def update_cpu_graph(data):
    if data is None:
        data = {'times': [], 'values': []}

    figure = {
        'data': [go.Scatter(
            x=data['times'],
            y=data['values'],
            mode='lines+markers',
            name='CPU Usage (%)'
        )],
        'layout': go.Layout(
            title='CPU Usage (%)',
            xaxis=dict(title='Time'),
            yaxis=dict(range=[0, 100], title='CPU Usage (%)'),
        )
    }
    return figure

# Callback to update Memory data store
@app.callback(
    Output('memory-data-store', 'data'),
    Input('interval-component', 'n_intervals'),
    State('memory-data-store', 'data')
)
def update_memory_data(n, data):
    time_now = datetime.datetime.now().strftime('%H:%M:%S')
    memory_percent = psutil.virtual_memory().percent

    if data is None:
        data = {'times': [], 'values': []}

    data['times'].append(time_now)
    data['values'].append(memory_percent)

    # Keep only the last 50 entries
    data['times'] = data['times'][-50:]
    data['values'] = data['values'][-50:]

    return data

# Callback to update Memory graph
@app.callback(
    Output('memory-usage-graph', 'figure'),
    Input('memory-data-store', 'data')
)
def update_memory_graph(data):
    if data is None:
        data = {'times': [], 'values': []}

    figure = {
        'data': [go.Scatter(
            x=data['times'],
            y=data['values'],
            mode='lines+markers',
            name='Memory Usage (%)'
        )],
        'layout': go.Layout(
            title='Memory Usage (%)',
            xaxis=dict(title='Time'),
            yaxis=dict(range=[0, 100], title='Memory Usage (%)'),
        )
    }
    return figure

# Callback to update Disk data store
@app.callback(
    Output('disk-data-store', 'data'),
    Input('interval-component', 'n_intervals'),
    State('disk-data-store', 'data')
)
def update_disk_data(n, data):
    time_now = datetime.datetime.now().strftime('%H:%M:%S')
    disk_percent = psutil.disk_usage('/').percent

    if data is None:
        data = {'times': [], 'values': []}

    data['times'].append(time_now)
    data['values'].append(disk_percent)

    # Keep only the last 50 entries
    data['times'] = data['times'][-50:]
    data['values'] = data['values'][-50:]

    return data

# Callback to update Disk graph
@app.callback(
    Output('disk-usage-graph', 'figure'),
    Input('disk-data-store', 'data')
)
def update_disk_graph(data):
    if data is None:
        data = {'times': [], 'values': []}

    figure = {
        'data': [go.Scatter(
            x=data['times'],
            y=data['values'],
            mode='lines+markers',
            name='Disk Usage (%)'
        )],
        'layout': go.Layout(
            title='Disk Usage (%)',
            xaxis=dict(title='Time'),
            yaxis=dict(range=[0, 100], title='Disk Usage (%)'),
        )
    }
    return figure

# Callback to update Network I/O data store
@app.callback(
    Output('network-data-store', 'data'),
    Input('interval-component', 'n_intervals'),
    State('network-data-store', 'data')
)
def update_network_data(n, data):
    time_now = datetime.datetime.now().strftime('%H:%M:%S')
    net_io = psutil.net_io_counters()
    bytes_sent = net_io.bytes_sent
    bytes_recv = net_io.bytes_recv

    if data is None:
        data = {
            'times': [],
            'bytes_sent': [],
            'bytes_recv': [],
            'last_bytes_sent': bytes_sent,
            'last_bytes_recv': bytes_recv
        }

    # Calculate bytes per interval
    sent_per_sec = bytes_sent - data.get('last_bytes_sent', bytes_sent)
    recv_per_sec = bytes_recv - data.get('last_bytes_recv', bytes_recv)

    data['times'].append(time_now)
    data['bytes_sent'].append(sent_per_sec)
    data['bytes_recv'].append(recv_per_sec)

    # Update last bytes sent and received
    data['last_bytes_sent'] = bytes_sent
    data['last_bytes_recv'] = bytes_recv

    # Keep only the last 50 entries
    data['times'] = data['times'][-50:]
    data['bytes_sent'] = data['bytes_sent'][-50:]
    data['bytes_recv'] = data['bytes_recv'][-50:]

    return data

# Callback to update Network I/O graph
@app.callback(
    Output('network-io-graph', 'figure'),
    Input('network-data-store', 'data')
)
def update_network_graph(data):
    if data is None:
        data = {'times': [], 'bytes_sent': [], 'bytes_recv': []}

    figure = {
        'data': [
            go.Scatter(
                x=data['times'],
                y=data['bytes_sent'],
                mode='lines+markers',
                name='Bytes Sent'
            ),
            go.Scatter(
                x=data['times'],
                y=data['bytes_recv'],
                mode='lines+markers',
                name='Bytes Received'
            )
        ],
        'layout': go.Layout(
            title='Network I/O (Bytes/sec)',
            xaxis=dict(title='Time'),
            yaxis=dict(title='Bytes per Second'),
        )
    }
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
