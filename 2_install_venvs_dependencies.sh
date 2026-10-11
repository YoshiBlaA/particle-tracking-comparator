#!/bin/bash
source v/bin/activate
pip install -r requirements.txt
deactivate
cd AdaptivePIV_3.7
source venv/bin/activate
pip install -r requirements.txt
deactivate
sleep
