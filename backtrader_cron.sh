#!/bin/bash

# Change to the correct directory
cd /home/ec2-user/main/backtrader_app

# Activate the virtual environment
source venv/bin/activate

# Run the Python script with the given argument
python main.py --RunBreakOut --RunAlgo_1

status=$?

# Deactivate the virtual environment
deactivate

# Output a message indicating whether the script ran successfully or not
if [ $status -eq 0 ]
then
    echo "Script ran successfully on $(date)"
else
    echo "Script failed to run on $(date)"
fi
