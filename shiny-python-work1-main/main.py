import pandas as pd
from shiny import App, reactive, render, ui
from server_ import *

app_ui = ui.output_ui("page")

app = App(app_ui, server)
app.run()
