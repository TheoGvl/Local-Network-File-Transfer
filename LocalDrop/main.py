import flet as ft
import os
import shutil
import qrcode
import socket
from network import get_local_ip
from server import start_server

def main_ui(page: ft.Page):
    # Window Styling - Expanded for a dashboard look
    page.title = "LocalDrop Control Center"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 800
    page.window.height = 550
    page.window.always_on_top = False 
    page.padding = 0
    page.window.resizable = False
    
    # --- System Stats Setup ---
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
    
    # Beautiful gradient background
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
                controls=[]
            )
        )
    )

    def handle_new_files(file_data):
        async def trigger_dialog():
            selected_dir = await ft.FilePicker().get_directory_path(
                dialog_title=f"Select folder to save {len(file_data)} file(s)"
            )
            
            if selected_dir:
                success_count = 0
                for temp_path, filename in file_data:
                    target_path = os.path.join(selected_dir, filename)
                    try:
                        shutil.copy2(temp_path, target_path)
                        success_count += 1
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                            
                        # Add successful transfer to the Live Activity Log
                        activity_log.controls.insert(0, ft.Container(
                            padding=10,
                            border_radius=8,
                            bgcolor="#1a252c",
                            content=ft.Row([
                                ft.Icon(ft.Icons.CHECK_CIRCLE, color="#00d2ff", size=20),
                                ft.Text(filename, size=14, color=ft.Colors.WHITE, expand=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
                            ])
                        ))
                    except Exception as ex:
                        print(f"Error saving {filename}: {ex}")
                        
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"✅ Successfully saved {success_count} file(s)!"), 
                    bgcolor=ft.Colors.TEAL_700,
                    behavior=ft.SnackBarBehavior.FLOATING,
                    margin=20
                )
                page.snack_bar.open = True
                
            else:
                for temp_path, _ in file_data:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                
            page.update()
            
        page.run_task(trigger_dialog)

    # --- Network & Server Setup ---
    port = 5000
    local_ip = get_local_ip()
    upload_url = f"http://{local_ip}:{port}"
    start_server(port, handle_new_files)

    # --- Generate Styled QR Code ---
    qr = qrcode.QRCode(box_size=12, border=1)
    qr.add_data(upload_url)
    qr.make(fit=True)
    qr_path = os.path.abspath("qr.png")
    img = qr.make_image(fill_color="#e0e0e0", back_color="#1a252c")
    img.save(qr_path)

    # --- UI Layout Assembly ---
    main_row = page.controls[0].content
    
    # LEFT CARD: Connection Details
    left_card = ft.Container(
        width=320,
        height=490,
        padding=30,
        border_radius=20,
        bgcolor="#66111111", 
        border=ft.border.all(1, "#19ffffff"),
        blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            controls=[
                ft.Icon(ft.Icons.WIFI_TETHERING, size=50, color="#00d2ff"),
                ft.Text("LocalDrop", size=28, weight=ft.FontWeight.W_900, color=ft.Colors.WHITE),
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=12, vertical=4),
                    border_radius=15,
                    bgcolor="#3300d2ff",
                    content=ft.Text(f"IP: {local_ip}", color="#00d2ff", weight=ft.FontWeight.BOLD, size=13)
                ),
                ft.Container(height=5),
                ft.Container(
                    padding=15,
                    border_radius=16,
                    bgcolor="#1a252c",
                    border=ft.border.all(2, "#19ffffff"),
                    content=ft.Image(src=qr_path, width=160, height=160)
                ),
                ft.Container(height=5),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.ProgressRing(width=14, height=14, stroke_width=2, color="#00d2ff"),
                        ft.Text("Active & Listening", italic=True, color=ft.Colors.WHITE54, size=13)
                    ]
                )
            ]
        )
    )

    # RIGHT CARD: System Stats & Logs
    right_card = ft.Container(
        width=360,
        height=490,
        padding=25,
        border_radius=20,
        bgcolor="#66111111",
        border=ft.border.all(1, "#19ffffff"),
        blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR),
        content=ft.Column(
            controls=[
                ft.Text("System Details", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Divider(color="#19ffffff", height=15),
                
                # Stats rows
                ft.Row([
                    ft.Icon(ft.Icons.COMPUTER, size=16, color="#b0bec5"),
                    ft.Text(f"Device: {hostname}", color="#b0bec5", size=13)
                ]),
                ft.Container(height=2),
                ft.Row([
                    ft.Icon(ft.Icons.STORAGE, size=16, color="#b0bec5"),
                    ft.Text(f"Free Space: {free_gb} GB", color="#b0bec5", size=13)
                ]),
                ft.Container(height=2),
                ft.Row([
                    ft.Icon(ft.Icons.ROUTER, size=16, color="#b0bec5"),
                    ft.Text(f"Port: {port} (TCP)", color="#b0bec5", size=13)
                ]),
                
                ft.Container(height=15),
                ft.Text("Recent Transfers", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Divider(color="#19ffffff", height=15),
                
                # The scrollable log
                ft.Container(
                    expand=True,
                    content=activity_log
                )
            ]
        )
    )
    
    main_row.controls.extend([left_card, right_card])
    page.update()

if __name__ == "__main__":
    ft.run(main_ui)