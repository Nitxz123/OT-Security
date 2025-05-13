from pymodbus.server.sync import ModbusTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock
import time
import threading

# ----------------- Modbus Data Store ------------------
# Use holding registers (hr) for read/write
store = ModbusSlaveContext(
    hr=ModbusSequentialDataBlock(0, [1]*100)  # water level at hr[0], pump at hr[1], valve at hr[2]
)
context = ModbusServerContext(slaves=store, single=True)

# ----------------- Water Level Logic ------------------
def simulate_water_system():
    while True:
        water_level = context[0].getValues(3, 0, count=1)[0]  # read hr[0]
        pump_status = context[0].getValues(3, 1, count=1)[0]  # read hr[1]
        valve_status = context[0].getValues(3, 2, count=1)[0]  # read hr[2]

        if pump_status:
            water_level += 1
        elif valve_status:
            water_level -= 1

        water_level = max(0, min(100, water_level))

        context[0].setValues(3, 0, [water_level])  # update hr[0]

        status = "Normal"
        if water_level > 90:
            status = "HIGH"
        elif water_level < 10:
            status = "LOW"

        print(f"[REAL PLC] Level: {water_level}% | Pump: {pump_status} | Valve: {valve_status} | Status: {status}")
        time.sleep(2)

# ----------------- Main ------------------
if __name__ == "__main__":
    print("[REAL PLC] Virtual PLC server running on port 1502 ...")
    threading.Thread(target=simulate_water_system, daemon=True).start()
    server = ModbusTcpServer(context, address=("0.0.0.0", 1502))
    server.serve_forever()

