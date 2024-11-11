# Data_over_sound

A Python program for transmitting and receiving data over sound waves using only a speaker and a microphone.

## Description

Data over Sound is a Python program that allows you to transmit and receive data between two devices using only a speaker and a microphone. This is especially useful when you don't have a network connection or a USB cable to transfer data between devices.

## How It Works

In very simple terms, the program splits the data into small chunks and encodes each chunk into a sound wave. Than it plays each sound wave through the speaker, and the receiving device listens to the sound waves through the microphone. The receiving device decodes the sound waves back into data and reconstructs the original piece of data.
This app leverages the Python library [ggwave](https://github.com/ggerganov/ggwave) by Georgi Gerganov. Many thanks to him for this library, which handles the sound-wave encoding and decoding!

## Installation

### Prerequisites

On **Windows**, ensure you set an environment variable to avoid installation issues with `ggwave`:

```cmd
set GGWAVE_USE_CYTHON=1
```

### Steps

1. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2. **Compile** (optional):
   - For **Windows**, run `compile.bat` or use the other platforms command below.
   - On other platforms, use:
     ```bash
     pyinstaller receiver.spec
     ```

## Usage

1. Run `main.py` on both devices and follow the device selection prompts.
2. If you hear the beeps from the selected output device, press Enter to confirm. If not, type "n" and press Enter to test another device. Repeat until both input and output devices are selected.
3. Once devices are selected, you’ll be in the command prompt. Type `/help` to see available commands.

## Commands

- type a message and press enter to send it (without slash prefix).
- **/help**: Displays a list of commands.
- **/p [protocol number] [payload length]**: Set protocol and payload length. Payload length is optional and must be between 4 and 64. It is only required for protocols 9 to 11 but can be set for all protocols.
- **/reset**: Reset the instance. If data starts to get corrupted, this command can be used to reset the instance.
- **/open**: Open URLs, emails, and phone numbers in the default web browser, email client, and phone dialer respectively. Use this command if a URL, email, or phone number is received. Use it at your own risk, as it may open malicious websites.
- **/stop**: Stop the program (not working properly, use Ctrl+C instead).
- **/exit**: Exit the program.
- **/device**: Test sound devices.
- **/sendhelp**: Sends each line of the help message as a separate message via sound.

## Protocols

The program supports 11 different protocols for encoding and decoding data. The protocols are as follows:
- **0 to 2**: dual tone, middle frequency, without error correction, from slowest (0) to fastest (2).
- **3 to 5**: dual tone, ultrasonic frequency, without error correction, from slowest (3) to fastest (5).
- **6 to 8**: dual tone, lowest frequency, with error correction, from slowest (6) to fastest (8).
- **9 to 11**: single tone, with error correction, from slowest (9) to fastest (11), requires payload length since no start and stop marker sounds are used.

## Contributing

Contributions are welcome! If you'd like to improve the code or add new features, please fork this repository, make your changes, and submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

Enjoy seamless, cable-free data transfers over sound waves!
