import dash
from dash import html

dash.register_page(
    __name__,
    path='/',
    redirect_from=['/home'],
    title='Home'
)

layout = html.Div(
    [
        html.H1('Home page!'),
        html.Div("This is just a placeholder for now. " 
                 "Use the navigation bar in the top to access the features of the app.")
    ]
)