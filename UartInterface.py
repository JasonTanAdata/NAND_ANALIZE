#!/usr/bin/env python3
"""
UART driver for Windows that connects a physical serial port to the project's
NANDAnalyzer.uart_interface(command_str) function.

Requirements:
  pip install pyserial

Usage (example):
  python uart_driver.py --port COM3 --baudrate 115200

If you run without --port it will list available COM ports and exit.
"""
import argparse
import threading
import json
import time
from typing import Optional

import serial  # pip install pyserial
import serial.tools.list_ports

from nand_analyzer import NANDAnalyzer


class UARTDriver:
    def __init__(self,
        port: str,
        baudrate: int = 115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout: float = 1.0,
        rtscts: bool = False,
        xonxoff: bool = False,
        newline: str = "\r\n",  # use CRLF on Windows by default
    ):
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self.rtscts = rtscts
        self.xonxoff = xonxoff
        self.newline = newline

        self._ser: Optional[serial.Serial] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.analyzer = NANDAnalyzer()

    def open(self):
        if self._ser and self._ser.is_open:
            return
        self._ser = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            bytesize=self.bytesize,
            parity=self.parity,
            stopbits=self.stopbits,
            timeout=self.timeout,
            rtscts=self.rtscts,
            xonxoff=self.xonxoff,
        )
        # small delay to let adapter settle
        time.sleep(0.1)

    def close(self):
        if self._ser:
            try:
                self._ser.close()
            except Exception:
                pass
            self._ser = None

    def start(self):
        """Start background thread that reads lines and responds."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self.open()
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop background thread and close port."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1.0)
        self.close()

    def send_line(self, line: str):
        """Send a line terminated with configured newline over UART."""
        if not self._ser or not self._ser.is_open:
            raise RuntimeError("Serial port not open")
        # Ensure proper line ending and encoding
        data = (line.rstrip("\r\n") + self.newline).encode("utf-8", errors="replace")
        self._ser.write(data)

    def _read_loop(self):
        """Read lines from serial, call analyzer, and write back JSON response."""
        ser = self._ser
        if not ser:
            return
        while not self._stop_event.is_set():
            try:
                raw = ser.readline()  # respects timeout
                if not raw:
                    continue
                try:
                    line = raw.decode("utf-8", errors="ignore").strip()
                except Exception:
                    line = raw.decode("latin1", errors="ignore").strip()

                if not line:
                    continue

                # Optionally echo the received command (useful for debugging)
                # self.send_line(f"RECV: {line}")

                # Pass command to NANDAnalyzer uart_interface and get dict result
                try:
                    result = self.analyzer.uart_interface(line)
                except Exception as e:
                    result = {"status": "error", "error": str(e)}

                # Convert result to JSON string and send back
                try:
                    out = json.dumps(result, ensure_ascii=False)
                except Exception:
                    out = str(result)

                self.send_line(out)
            except Exception:
                # small sleep to avoid busy loop on persistent errors
                time.sleep(0.1)
                continue


def list_com_ports():
    ports = list(serial.tools.list_ports.comports())
    return ports


def main():
    parser = argparse.ArgumentParser(description="UART driver for NANDAnalyzer (Windows).")
    parser.add_argument("--port", "-p", help="Serial port (e.g. COM3). If omitted the program lists available ports and exits.")
    parser.add_argument("--baudrate", "-b", type=int, default=115200, help="Baud rate (default 115200)")
    parser.add_argument("--timeout", "-t", type=float, default=1.0, help="Read timeout in seconds")
    parser.add_argument("--rtscts", action="store_true", help="Enable RTS/CTS hardware flow control")
    parser.add_argument("--xonxoff", action="store_true", help="Enable XON/XOFF software flow control")
    args = parser.parse_args()

    if not args.port:
        print("Available serial ports:")
        for p in list_com_ports():
            print(f"  {p.device} - {p.description}")
        print("\nRun with --port <PORT> to start the driver (e.g. --port COM3).")
        return

    driver = UARTDriver(
        port=args.port,
        baudrate=args.baudrate,
        timeout=args.timeout,
        rtscts=args.rtscts,
        xonxoff=args.xonxoff,
        newline="\r\n",
    )

    try:
        print(f"Opening {args.port} at {args.baudrate} bps...")
        driver.start()
        print("Driver started. Press Ctrl-C to stop.")
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("Stopping driver...")
    finally:
        driver.stop()
        print("Driver stopped.")


if __name__ == "__main__":
    main()
