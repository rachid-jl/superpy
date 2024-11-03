import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import plotly.graph_objs as go
import psutil
import datetime

app = dash.Dash(__name__)
app.title = 'System Monitoring Dashboard'

def get_system_metrics():
    metrics = {
        'cpu_percent': psutil.cpu_percent(interval=None),
        'memory': psutil.virtual_memory(),
        'disk': psutil.disk_usage('/'),
        'net_io': psutil.net_io_counters(),
    }
    return metrics

app.layout = html.Div(children=[
    html.H1('System Monitoring Dashboard', style={'textAlign': 'center'}),

    html.Div(id='live-update-text', style={'textAlign': 'center'}),

    dcc.Graph(id='cpu-usage-graph'),
    dcc.Graph(id='memory-usage-graph'),
    dcc.Graph(id='disk-usage-graph'),
    dcc.Graph(id='network-io-graph'),

    dcc.Interval(
        id='interval-component',
        interval=2*1000,  # Update every 2 seconds
        n_intervals=0
    )
])

@app.callback(Output('live-update-text', 'children'),
              Input('interval-component', 'n_intervals'))
def update_metrics(n):
    metrics = get_system_metrics()
    style = {'padding': '5px', 'fontSize': '20px'}

    return [
        html.Span(f"CPU Usage: {metrics['cpu_percent']}%", style=style),
        html.Br(),
        html.Span(f"Memory Usage: {metrics['memory'].percent}%", style=style),
        html.Br(),
        html.Span(f"Disk Usage: {metrics['disk'].percent}%", style=style),
    ]

@app.callback(Output('cpu-usage-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_cpu_graph(n):
    time = datetime.datetime.now()
    cpu_percent = psutil.cpu_percent()

    if 'cpu_data' not in dash.callback_context._cache:
        dash.callback_context._cache['cpu_data'] = {'times': [], 'values': []}

    data = dash.callback_context._cache['cpu_data']
    data['times'].append(time)
    data['values'].append(cpu_percent)

    data['times'] = data['times'][-50:]
    data['values'] = data['values'][-50:]

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

@app.callback(Output('memory-usage-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_memory_graph(n):
    time = datetime.datetime.now()
    memory = psutil.virtual_memory().percent

    if 'memory_data' not in dash.callback_context._cache:
        dash.callback_context._cache['memory_data'] = {'times': [], 'values': []}

    data = dash.callback_context._cache['memory_data']
    data['times'].append(time)
    data['values'].append(memory)

    data['times'] = data['times'][-50:]
    data['values'] = data['values'][-50:]

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

@app.callback(Output('disk-usage-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_disk_graph(n):
    time = datetime.datetime.now()
    disk = psutil.disk_usage('/').percent

    if 'disk_data' not in dash.callback_context._cache:
        dash.callback_context._cache['disk_data'] = {'times': [], 'values': []}

    data = dash.callback_context._cache['disk_data']
    data['times'].append(time)
    data['values'].append(disk)

    data['times'] = data['times'][-50:]
    data['values'] = data['values'][-50:]

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

@app.callback(Output('network-io-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_network_graph(n):
    time = datetime.datetime.now()
    net_io = psutil.net_io_counters()

    if 'network_data' not in dash.callback_context._cache:
        dash.callback_context._cache['network_data'] = {
            'times': [],
            'bytes_sent': [],
            'bytes_recv': [],
            'last_net_io': net_io
        }

    data = dash.callback_context._cache['network_data']
    bytes_sent = net_io.bytes_sent - data['last_net_io'].bytes_sent
    bytes_recv = net_io.bytes_recv - data['last_net_io'].bytes_recv

    data['times'].append(time)
    data['bytes_sent'].append(bytes_sent)
    data['bytes_recv'].append(bytes_recv)
    data['last_net_io'] = net_io

    data['times'] = data['times'][-50:]
    data['bytes_sent'] = data['bytes_sent'][-50:]
    data['bytes_recv'] = data['bytes_recv'][-50:]

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
