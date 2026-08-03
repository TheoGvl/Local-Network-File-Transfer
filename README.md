# LocalDrop

LocalDrop is a sleek, modern, and lightning-fast local network file transfer application. It bridges your mobile device and your PC securely over Wi-Fi Direct, entirely eliminating the need for cables, cloud services, or internet connectivity. 

Built with **Python**, featuring a beautiful glassmorphism dashboard powered by **Flet** (PC) and a dark-mode mobile web interface powered by **Flask** (Mobile).

## Features
* **Zero-Setup Connection:** Automatically detects your local IP and generates a scannable QR code on your PC screen.
* **Modern Dashboard:** A real-time, responsive UI on the desktop displaying connection status, device hostname, available storage, and a live activity log.
* **Batch Transfers:** Select and send multiple files (photos, PDFs, videos, documents) simultaneously from your phone.
* **Smart Destination Picker:** PC prompts you once to select a target directory, then securely copies all incoming files automatically.
* **Premium UI/UX:** Features a custom dark theme, ARGB glassmorphism effects, dynamic status indicators, and clean UI components.

## Tech Stack
* **Frontend (Desktop):** Flet (Flutter for Python)
* **Backend & Mobile UI:** Flask
* **Networking/QR:** `socket`, `qrcode`

## Prerequisites
Make sure you have Python 3 installed on your system. You will also need to install the required libraries:

```
pip install flet flask qrcode pillow
```
## How to Use
Clone or download this repository to your local machine.
Ensure both your PC and your mobile device are connected to the same Wi-Fi network.
Run the application from your terminal:
```
python main.py
```
A dashboard will open on your PC displaying a QR code.

Scan the QR code with your phone's camera to open the LocalDrop web app.

Select the files you want to transfer and tap "Send to Dashboard".

On your PC, pick a folder, and your files will be instantly saved!

## Security & Privacy
LocalDrop operates 100% locally on your network. No data is ever routed through external servers or the internet. 
All temporary files are automatically cleaned up from your system after a successful (or cancelled) transfer.
