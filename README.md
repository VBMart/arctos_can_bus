# arctos_can_bus

## Description
`arctos_can_bus` is a Python-based project for interfacing with a robot via the CAN bus. The main file includes test functions for movement and encoder reading.

### Implemented Features
- **X, Y, Z Movement**: Currently, only movement in X, Y, and Z directions is implemented.
- **Encoder Reading**: Safely checks motor connections by reading encoder values.
- **Movement Testing**: Sends movement commands to the robot in the X direction.
- **Homing Functionality**: Moves the robot to its home position.

### Available Commands
```sh
python3 main.py read_encoders   # Reads encoder values from the CAN bus
python3 main.py test_x_run      # Moves the robot in the X direction
python3 main.py go_home         # Moves the robot to its home position
```

## Environment Setup
### 1. Create a Virtual Environment
```sh
python3 -m venv ~/myenv/arc
```

### 2. Activate the Virtual Environment
```sh
source ~/myenv/arc/bin/activate
```

### 3. Install Dependencies
Navigate to the directory containing `requirements.txt` and install required packages:
```sh
pip install -r requirements.txt
```

### 4. Deactivate Virtual Environment
To exit the virtual environment, run:
```sh
deactivate
```