# arctos_can_bus

## Description
Main file contains some test functions. 
Only X, Y, Z are implemented at the moment. 
`python3 main.py read_encoders` reads the encoder values from the CAN bus (Safest way to check connections with motor).
`python3 main.py test_x_run` sends movement commands to the robot in the X direction.
`python3 main.py go_home` sends the robot to the home position.

## Prepare the environment
1. Create a virtual environment:
`python3 -m venv ~/myenv/arc`

2. Activate the virtual environment:
`source ~/myenv/arc/bin/activate`

3. Install required packages (go to the directory where the requirements.txt file is located):
`pip install -r requirements.txt`

4. To exit the virtual environment, use:
`deactivate`