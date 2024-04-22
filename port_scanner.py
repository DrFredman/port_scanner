import socket as s
import argparse
import threading
import sys

class PortScanner:
    def __init__(self):
        self.options = self.get_arguments()

    def get_arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-i", "--target", dest="target", help="Target IP address", default="127.0.0.1")
        parser.add_argument("-t", "--threads", dest="threads", help="Number of threads", default=10, type=int)
        parser.add_argument("-p", "--ports", dest="end_port", help="Highest port to scan", default=1000, type=int)
        parser.add_argument("-w", "--timeout", dest="timeout", help="Number of seconds to wait until timing out a connection", default=1, type=int)
        options = parser.parse_args()
        return options

    def scan(self, target, start_port, end_port, timeout, stop_event, open_ports, closed_ports):
        try:
            for port in range(start_port, end_port + 1):
                if stop_event.is_set():
                    break
                con = s.socket(s.AF_INET, s.SOCK_STREAM)
                con.settimeout(timeout)
                try:
                    con.connect((target, port))
                    con.send(b"Hello")
                    response = con.recv(1024)
                    if response:
                        open_ports.increment()
                        print("Discovered port", port, "is open. ")
                    else:
                        closed_ports.increment()
                except s.error:
                    closed_ports.increment()
                finally:
                    con.close()
        except KeyboardInterrupt:
            stop_event.set()

    class Counter:
        def __init__(self):
            self.value = 0
            self.lock = threading.Lock()

        def increment(self):
            with self.lock:
                self.value += 1

        def get_value(self):
            with self.lock:
                return self.value


    def main(self, target, thread_count, end_port, timeout):
        threads = []
        start_port = 1
        ports_per_thread = (end_port - start_port + 1) // thread_count

        stop_event = threading.Event()
        open_ports = self.Counter()
        closed_ports = self.Counter()

        for index in range(thread_count):
            start = start_port + index * ports_per_thread
            end = start_port + (index + 1) * ports_per_thread - 1
            if index == thread_count - 1:
                end = end_port
            x = threading.Thread(target=self.scan, args=(target, start, end, timeout, stop_event, open_ports, closed_ports))
            threads.append(x)
            x.start()


        # Join all threads
        for thread in threads:
            thread.join()


        open_ports_count = open_ports.get_value()
        closed_ports_count = closed_ports.get_value()
        all_closed_ports = closed_ports_count - open_ports_count
        print("Port scanning stopped.")
        sys.exit()
