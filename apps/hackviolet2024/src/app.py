from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
import requests
import subprocess

# Create a Dash application using the Flask server
app = Dash(__name__)

# Define the layout of the Dash app with system-ui font and rounded corners for the input
app.layout = html.Div([
    html.Div([
        dcc.Input(
            id='input-topic',
            type='text',
            placeholder='Enter a topic...',
            style={'width': '60%', 'height': '40px', 'fontSize': '20px', 'textAlign': 'center', 'fontFamily': 'system-ui', 'fontWeight': 'bold', 'overflow': 'hidden', 'borderRadius': '20px'}  # Added borderRadius property
        ),
        html.Button(
            'Submit',
            id='play-button',
            n_clicks=0,
            style={'width': '10%', 'height': '46px', 'fontSize': '20px', 'marginLeft': '5px', 'fontFamily': 'system-ui', 'fontWeight': 'bold', 'borderRadius': '20px'}
        )
    ], style={'textAlign': 'center', 'marginTop': '20%', 'fontFamily': 'system-ui'}),
    html.Div(id='output-container-button', children='Enter a topic and press play',
             style={'textAlign': 'center', 'marginTop': '20px', 'fontSize': '20px', 'fontFamily': 'system-ui', 'fontWeight': 'bold', 'color': 'white'})
], style={'background-image': 'linear-gradient(#272727, #9198e5)',
          'width': '100vw',
          'height': '100vh',
          'position': 'absolute',
          'left': '0',
          'top': '0',
          'fontFamily': 'system-ui'})

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
            subprocess.Popen(['python', 'apps/backend/main.py'])
            return f"Possible trigger words: {', '.join(map(str, result))}"
        else:
            return "Failed to perform action."
    return 'Enter a topic and press submit'

if __name__ == '__main__':
    app.run_server(debug=True, port=8000)
