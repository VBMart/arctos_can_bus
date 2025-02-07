import can
import time
from typing import List

from constants import CMD_READ_ENCODER, CMD_GO_HOME, CMD_SET_ENABLE, CMD_REMAP, CMD_RELATIVE_TURN


def can_send_message(bus: can.interface.Bus, message: can.Message) -> None:
    bus.send(message)
    data_bytes = ", ".join([f"0x{byte:02X}" for byte in message.data])
    print(
        f"Message sent: arbitration_id=0x{message.arbitration_id:X}, data=[{data_bytes}], is_extended_id=False"
    )


def can_send_message_and_wait_response(bus: can.interface.Bus, message: can.Message, timeout = 0.5) -> List:
    received_responses = []

    command = message.data[0]
    bus.send(message)
    data_bytes = ", ".join([f"0x{byte:02X}" for byte in message.data])
    print(
        f"Message sent: arbitration_id=0x{message.arbitration_id:X}, data=[{data_bytes}], is_extended_id=False"
    )

    if timeout == 0:
        return received_responses

    start_time = time.time()
    while True:
        received_msg = bus.recv(timeout=min(timeout, 1))
        if received_msg is not None:
            received_data_bytes = ", ".join(
                [f"0x{byte:02X}" for byte in received_msg.data]
            )
            print(
                f"Received: arbitration_id=0x{received_msg.arbitration_id:X}, data=[{received_data_bytes}], is_extended_id=False"
            )
            received_responses.append(received_msg)
            if message.arbitration_id == received_msg.arbitration_id:
                if received_msg.data[0] == message.data[0]:
                    if command == CMD_READ_ENCODER:
                        carry_bytes = received_msg.data[1:5]
                        carry = int.from_bytes(carry_bytes, byteorder='big', signed=True)
                        rot = carry
                        value_bytes = received_msg.data[5:7]
                        value = int.from_bytes(value_bytes, byteorder='big', signed=False)
                        max_value = 0x3FFF
                        degrees = 360 * (value / max_value)
                        print(f'Got encoder value: carry={carry}, value={value} -> degrees: {degrees}, rotation: {rot}')
                        break
                    if command == CMD_GO_HOME:
                        status = received_msg.data[1]
                        if status == 0x01:
                            print('Home started')
                        elif status == 0x02:
                            print('Home found')
                            break
                        elif status == 0x00:
                            print('Home failed')
                            break
                    if command == CMD_SET_ENABLE:
                        status = received_msg.data[1]
                        if status == 0x01:
                            print('Enable success')
                        elif status == 0x00:
                            print('Enable failed')
                            break
                    if command == CMD_REMAP:
                        status = received_msg.data[1]
                        if status == 0x01:
                            print('Remap success')
                        elif status == 0x00:
                            print('Remap failed')
                            break
                    if command == CMD_RELATIVE_TURN:
                        status = received_msg.data[1]
                        if status == 0x01:
                            print('Motor started')
                        elif status == 0x02:
                            print('Motor stopped')
                            break
                        elif status == 0x00:
                            print('Motor failed')
                            break
                        elif status == 0x03:
                            print('Motor found endstop')
                            break
                else:
                    print('Got response for another message')
            else:
                print('Got message from another device')

        if time.time() - start_time > timeout:
            print("Timeout waiting for responses.")
            break

    print('')
    return received_responses

def print_motor_message(message: can.Message) -> None:
    command = message.data[0]
    if command == CMD_READ_ENCODER:
        carry_bytes = message.data[1:5]
        carry = int.from_bytes(carry_bytes, byteorder='big', signed=True)
        rot = carry
        value_bytes = message.data[5:7]
        value = int.from_bytes(value_bytes, byteorder='big', signed=False)
        max_value = 0x3FFF
        degrees = 360 * (value / max_value)
        print(f'Got encoder value: carry={carry}, value={value} -> degrees: {degrees}, rotation: {rot}')
    if command == CMD_GO_HOME:
        status = message.data[1]
        if status == 0x01:
            print('Home started')
        elif status == 0x02:
            print('Home found')
        elif status == 0x00:
            print('Home failed')
    if command == CMD_SET_ENABLE:
        status = message.data[1]
        if status == 0x01:
            print('Enable success')
        elif status == 0x00:
            print('Enable failed')
    if command == CMD_REMAP:
        status = message.data[1]
        if status == 0x01:
            print('Remap success')
        elif status == 0x00:
            print('Remap failed')
    if command == CMD_RELATIVE_TURN:
        status = message.data[1]
        if status == 0x01:
            print('Motor started')
        elif status == 0x02:
            print('Motor stopped')
        elif status == 0x00:
            print('Motor failed')
        elif status == 0x03:
            print('Motor found endstop')

def calc_checksum(can_id, data) -> int:
    sm = can_id
    for n in data:
        sm += n
    return (sm) & 0xFF

def make_message(can_id, data) -> can.Message:
    data.append(calc_checksum(can_id, data))
    return can.Message(arbitration_id=can_id, data=data, is_extended_id=False)
