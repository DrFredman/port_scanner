from port_scanner import PortScanner

def main():
    # Define input arguments
    target = "127.0.0.1"
    thread_count = 100
    end_port = 1000
    timeout = 2

    # Create an instance of the PortScanner class
    scanner = PortScanner()
    
    # Run the port scanning process
    scanner.main(target, thread_count, end_port, timeout)

if __name__ == "__main__":
    main()