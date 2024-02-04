from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
import requests

# Create a Dash application using the Flask server
app = Dash(__name__)

# Define the layout of the Dash app as before
app.layout = html.Div([
    html.Div([
        dcc.Input(
            id='input-topic',
            type='text',
            placeholder='Enter a topic...',
            style={'width': '60%', 'height': '40px', 'fontSize': '20px', 'textAlign': 'center'}
        ),
        html.Button(
            'Play',
            id='play-button',
            n_clicks=0,
            style={'width': '10%', 'height': '46px', 'fontSize': '20px', 'marginLeft': '5px'}
        )
    ], style={'textAlign': 'center', 'marginTop': '20%'}),
    html.Div(id='output-container-button', children='Enter a topic and press play',
             style={'textAlign': 'center', 'marginTop': '20px', 'fontSize': '20px'})
], style={'background-image': 'linear-gradient(#272727, #9198e5)',
          'width': '100vw',
          'height': '100vh',
          'position': 'absolute',
          'left': '0',
          'top': '0'})

# Example callback that makes an HTTP POST request to the Flask route
@app.callback(
    Output('output-container-button', 'children'),
    [Input('play-button', 'n_clicks')],
    [State('input-topic', 'value')]
)

def update_output(n_clicks, value):
    if n_clicks > 0:
        response = requests.post('https://hack-violet-backend.vercel.app/generate', json={'topic': value})
        if response.ok:
            result = response.json()
            print(result)
            return "success"
        else:
            return "Failed to perform action."
    return 'Enter a topic and press play'

if __name__ == '__main__':
    app.run_server(debug=True, port=8000)
