import flet as ft
import os
import shutil
import qrcode
import socket
import tkinter as tk
from tkinter import filedialog
import ctypes
from network import get_local_ip
import server

# Enhance UI rendering clarity on high-DPI displays
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

def main_ui(page: ft.Page):
    # Configure application window properties and thematic elements
    page.title = "LocalDrop Control Center"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 800
    page.window.height = 570
    page.window.always_on_top = False 
    page.padding = 0
    page.window.resizable = False
    
    # Initialize system telemetry and storage capacity metrics
    hostname = socket.gethostname()
    try:
        total, used, free = shutil.disk_usage(os.path.expanduser("~"))
        free_gb = free // (2**30)
    except:
        free_gb = "N/A"
        
    activity_log = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=10
    )
    
    current_file_data = []

    # Subroutine: Native directory selection for incoming payloads
    def open_save_picker(e):
        incoming_dialog.open = False
        page.update()
        
        # Isolate and elevate native tkinter directory selection interface
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        selected_dir = filedialog.askdirectory(title=f"Select folder to save {len(current_file_data)} file(s)")
        root.destroy()

        if selected_dir:
            success_count = 0
            for temp_path, filename in current_file_data:
                target_path = os.path.join(selected_dir, filename)
                try:
                    shutil.copy2(temp_path, target_path)
                    success_count += 1
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        
                    activity_log.controls.insert(0, ft.Container(
                        padding=10,
                        border_radius=8,
                        bgcolor="#1a252c",
                        content=ft.Row([
                            ft.Icon(ft.Icons.CHECK_CIRCLE, color="#00d2ff", size=20),
                            ft.Text(f"Received: {filename}", size=14, color=ft.Colors.WHITE, expand=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
                        ])
                    ))
                except Exception as ex:
                    print(f"Error saving {filename}: {ex}")
                    
            snack = ft.SnackBar(
                content=ft.Text(f"✅ Successfully saved {success_count} file(s)!"), 
                bgcolor=ft.Colors.TEAL_700,
                behavior=ft.SnackBarBehavior.FLOATING,
                margin=20
            )
            page.overlay.append(snack)
            snack.open = True  # type: ignore
            
        else:
            for temp_path, _ in current_file_data:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        current_file_data.clear()
        page.update()

    def cancel_save(e):
        incoming_dialog.open = False
        for temp_path, _ in current_file_data:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        current_file_data.clear()
        page.update()

    incoming_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row([ft.Icon(ft.Icons.DOWNLOAD_ROUNDED, color="#00d2ff"), ft.Text("Incoming Files!")]),
        content=ft.Text("Your mobile device sent files. Where would you like to save them?"),
        actions=[
            ft.TextButton("Save Files", on_click=open_save_picker, style=ft.ButtonStyle(color="#00d2ff")),
            ft.TextButton("Cancel", on_click=cancel_save, style=ft.ButtonStyle(color=ft.Colors.GREY_400))
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor="#1a252c",
        shape=ft.RoundedRectangleBorder(radius=15),
    )
    
    page.overlay.append(incoming_dialog)

    # Subroutine: Native file selection for outbound sharing
    def open_file_picker(e):
        # Isolate and elevate native tkinter file selection interface
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        file_paths = filedialog.askopenfilenames(title="Select files to share to Mobile")
        root.destroy()
        
        if file_paths:
            for file_path in file_paths:
                filename = os.path.basename(file_path)
                server.shared_files[filename] = file_path
                
                activity_log.controls.insert(0, ft.Container(
                    padding=10,
                    border_radius=8,
                    bgcolor="#1a252c",
                    border=ft.Border(
                        top=ft.BorderSide(1, "#3a7bd5"),
                        bottom=ft.BorderSide(1, "#3a7bd5"),
                        left=ft.BorderSide(1, "#3a7bd5"),
                        right=ft.BorderSide(1, "#3a7bd5")
                    ),
                    content=ft.Row([
                        ft.Icon(ft.Icons.UPLOAD_FILE, color="#3a7bd5", size=20),
                        ft.Text(f"Shared: {filename}", size=14, color=ft.Colors.WHITE, expand=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
                    ])
                ))
            
            snack = ft.SnackBar(
                content=ft.Text(f"🚀 {len(file_paths)} file(s) ready for mobile download!"), 
                bgcolor=ft.Colors.BLUE_700,
                behavior=ft.SnackBarBehavior.FLOATING,
                margin=20
            )
            page.overlay.append(snack)
            snack.open = True  # type: ignore
            page.update()

    # Implement thread-safe Publish-Subscribe messaging protocol
    def on_pubsub_message(message):
        current_file_data.clear()
        current_file_data.extend(message)
        incoming_dialog.open = True
        page.update()

    page.pubsub.subscribe(on_pubsub_message)

    def handle_new_files(file_data):
        page.pubsub.send_all(file_data)

    # Initialize network socket configurations and generate access QR code
    port = 5000
    local_ip = get_local_ip()
    upload_url = f"http://{local_ip}:{port}"
    server.start_server(port, handle_new_files)

    qr = qrcode.QRCode(box_size=12, border=1)
    qr.add_data(upload_url)
    qr.make(fit=True)
    qr_path = os.path.abspath("qr.png")
    img = qr.make_image(fill_color="#e0e0e0", back_color="#1a252c")
    img.save(qr_path)  # type: ignore

    # Construct primary user interface layout and visual hierarchies
    border_style = ft.Border(
        top=ft.BorderSide(1, "#19ffffff"),
        right=ft.BorderSide(1, "#19ffffff"),
        bottom=ft.BorderSide(1, "#19ffffff"),
        left=ft.BorderSide(1, "#19ffffff")
    )
    
    share_btn = ft.Container(
        height=45, 
        content=ft.Row(
            [
                ft.Icon(ft.Icons.UPLOAD_FILE, color=ft.Colors.WHITE, size=18),
                ft.Text("Share to Mobile", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
            ],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        bgcolor="#3a7bd5",
        border_radius=8,
        padding=ft.Padding(left=20, right=20, top=10, bottom=10),
        on_click=open_file_picker
    )
    
    left_card = ft.Container(
        width=320,
        height=510,
        padding=25,
        border_radius=20,
        bgcolor="#66111111", 
        border=border_style,
        blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.WIFI_TETHERING, size=40, color="#00d2ff"),
                ft.Text("LocalDrop", size=26, weight=ft.FontWeight.W_900, color=ft.Colors.WHITE),
                ft.Container(
                    padding=ft.Padding(left=12, right=12, top=4, bottom=4),
                    border_radius=15,
                    bgcolor="#3300d2ff",
                    content=ft.Text(f"IP: {local_ip}", color="#00d2ff", weight=ft.FontWeight.BOLD, size=13)
                ),
                ft.Container(height=5),
                ft.Container(
                    padding=15,
                    border_radius=16,
                    bgcolor="#1a252c",
                    border=ft.Border(
                        top=ft.BorderSide(2, "#19ffffff"),
                        right=ft.BorderSide(2, "#19ffffff"),
                        bottom=ft.BorderSide(2, "#19ffffff"),
                        left=ft.BorderSide(2, "#19ffffff")
                    ),
                    content=ft.Image(src=qr_path, width=150, height=150)
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.ProgressRing(width=14, height=14, stroke_width=2, color="#00d2ff"),
                        ft.Text("Active & Listening", italic=True, color=ft.Colors.WHITE54, size=13)
                    ]
                ),
                ft.Container(height=5),
                share_btn
            ]
        )
    )

    right_card = ft.Container(
        width=360,
        height=510,
        padding=25,
        border_radius=20,
        bgcolor="#66111111",
        border=border_style,
        blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR),
        content=ft.Column(
            controls=[
                ft.Text("System Details", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Divider(color="#19ffffff", height=15),
                ft.Row([ft.Icon(ft.Icons.COMPUTER, size=16, color="#b0bec5"), ft.Text(f"Device: {hostname}", color="#b0bec5", size=13)]),
                ft.Container(height=2),
                ft.Row([ft.Icon(ft.Icons.STORAGE, size=16, color="#b0bec5"), ft.Text(f"Free Space: {free_gb} GB", color="#b0bec5", size=13)]),
                ft.Container(height=2),
                ft.Row([ft.Icon(ft.Icons.ROUTER, size=16, color="#b0bec5"), ft.Text(f"Port: {port} (TCP)", color="#b0bec5", size=13)]),
                ft.Container(height=15),
                ft.Text("Live Activity", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Divider(color="#19ffffff", height=15),
                ft.Container(expand=True, content=activity_log)
            ]
        )
    )
    
    page.add(
        ft.Container(
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1.0, -1.0),
                end=ft.Alignment(1.0, 1.0),
                colors=["#0f2027", "#203a43", "#2c5364"]
            ),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=30,
                controls=[left_card, right_card]
            )
        )
    )

if __name__ == "__main__":
    ft.run(main_ui)