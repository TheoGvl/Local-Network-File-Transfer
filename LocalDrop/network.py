import socket

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # it simply "tries" to see which network card it would come out from., 
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

# this function can be used to get the local IP address of the machine running the script. 
# It creates a UDP socket and attempts to connect to a non-routable IP address, which allows it to determine the local IP without sending any data. If it fails, it defaults to '
if __name__ == "__main__":
    print(f"Η τοπική IP του υπολογιστή είναι: {get_local_ip()}")