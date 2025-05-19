from pymodbus.server.sync import ModbusTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock
import logging
import time
import threading
import os

# ----------------- Logging Setup ------------------
logging.basicConfig(
    filename="honeypot_log.txt",
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# ----------------- Modbus Context ------------------
water_level_block = ModbusSequentialDataBlock(0, [50])
store = ModbusSlaveContext(hr=water_level_block)
context = ModbusServerContext(slaves=store, single=True)

# ----------------- Global Override ------------------
attack_override = False
override_level = 50

# ----------------- Water Level Simulation ------------------
def simulate_water_level():
    global attack_override, override_level
    level = 50
    increasing = True
    while True:
        if not attack_override:
            level = level + 1 if increasing else level - 1
            if level >= 100:
                increasing = False
            elif level <= 20:
                increasing = True
            context[0].setValues(3, 0, [level])
        else:
            context[0].setValues(3, 0, [override_level])

        water_level = context[0].getValues(3, 0)[0]
        alarm_status = 1 if water_level > 90 else 0
        status = "ALARM! HIGH WATER LEVEL" if alarm_status else "Water Level Normal"
        print(f"[INFO] {status}: {water_level}%")
        logging.info(f"[INFO] {status}: {water_level}%")
        time.sleep(2)

# ----------------- Monitor for Write Attacks ------------------
def monitor_for_attacks():
    global attack_override, override_level
    last_level = 50
    while True:
        current_level = context[0].getValues(3, 0)[0]
        if abs(current_level - last_level) > 5:
            override_level = current_level
            attack_override = True
            logging.warning(f"[OVERRIDE DETECTED] Water level forcibly set to {current_level}%")
            print(f"[ALERT] Attacker override detected: {current_level}%")
        last_level = current_level
        time.sleep(1)

# ----------------- Custom Modbus Server with IP Logging ------------------
class HoneypotModbusTcpServer(ModbusTcpServer):
    def finish_request(self, request, client_address):
        ip = client_address[0]
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[CONNECTION] Client connected from {ip}")
        logging.info(f"[CONNECTION] Client connected from {ip}")

        filename = "attackers.txt"
        if not os.path.exists(filename):
            open(filename, "w").close()

        with open(filename, "r") as f:
            known_ips = [line.strip().split(" - ")[-1] for line in f if " - " in line]

        if ip not in known_ips:
            with open(filename, "a") as f:
                f.write(f"{timestamp} - {ip}\n")
            logging.info(f"[NEW ATTACKER] Logged new IP: {ip}")
            print(f"[NEW ATTACKER] Logged new IP: {ip}")

        super().finish_request(request, client_address)

# ----------------- Run Everything ------------------
if __name__ == "__main__":
    print("[HONEYPOT] Water Tank PLC Honeypot is running on port 5020 ...")
    threading.Thread(target=simulate_water_level, daemon=True).start()
    threading.Thread(target=monitor_for_attacks, daemon=True).start()

    server = HoneypotModbusTcpServer(
        context,
        address=("0.0.0.0", 5020)
    )
    server.serve_forever()
