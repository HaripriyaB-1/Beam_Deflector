# Beam Deflection Calculator

I built this to actually see what's happening in the beam problems 
from my Mechanics of Materials class — instead of just plugging into 
a formula, you can move the load around and watch the diagrams change.

Live: https://beamdeflector-27.streamlit.app

## What it does

Takes beam length, section properties, and load inputs and plots the 
shear force diagram, bending moment diagram, and deflection curve. 
Includes real steel section presets so you're not making up I values.

Validated against a textbook problem from Hibbeler — max deflection 
came out to 130.21 mm against the analytical answer of 130.21 mm.

## Stack
Python · NumPy · Matplotlib · Streamlit

## Run it locally
pip install -r requirements.txt  
streamlit run app.py
