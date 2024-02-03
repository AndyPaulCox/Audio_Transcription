import sounddevice as sd

def find_device_id(device_name):
    devices = sd.query_devices()
    for device in devices:
        if device['name'] == device_name:
            return device['index']  # Return the device ID
    return None

device_name = "MacBook Air Microphone"  # Example device name
device_id = find_device_id(device_name)

if device_id is not None:
    print(f"Device ID for '{device_name}': {device_id}")
else:
    print(f"Device '{device_name}' not found.")
