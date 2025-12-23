import requests
import time
import datetime
import os

# --- CONFIGURATION ---
# Get your key from: https://rapidapi.com/cnorris1316/api/gridwatch-us-telemetry
RAPIDAPI_KEY = "YOUR_RAPIDAPI_KEY_HERE"

# Region Options: PJM, MISO, ERCOT, SPP, NYISO, ISO-NE, CAISO
REGION = "ERCOT"

# Safety Thresholds
PRICE_CAP = 200        # Shut down if price > $200/MWh
STRESS_CAP = 90        # Shut down if grid stress > 90%

# Simulation Mode (Set to False to actually execute shutdown commands)
SIMULATION_MODE = True

def stop_mining_rigs():
    """
    Place your specific shutdown logic here.
    Examples:
    - Call a smart plug API (Kasa/Shelly)
    - SSH into a management node
    - Execute a local shell command
    """
    print("   [ACTION] 🛑 SENDING SHUTDOWN SIGNAL TO RIGS...")

def check_grid_status():
    url = "https://gridwatch-us-telemetry.p.rapidapi.com/api/curtailment"

    querystring = {
        "region": REGION,
        "price_cap": str(PRICE_CAP),
        "stress_cap": str(STRESS_CAP)
    }

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "gridwatch-us-telemetry.p.rapidapi.com"
    }

    try:
        print(f"Checking {REGION} grid status...", end="\r")
        response = requests.get(url, headers=headers, params=querystring, timeout=10)

        if response.status_code != 200:
            print(f"\n❌ API Error: {response.status_code} - {response.text}")
            return

        data = response.json()
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        # --- LOGIC ---
        if data.get('curtail'):
            print(f"\n[{timestamp}] 🔴 CURTAILMENT SIGNAL RECEIVED!")
            print(f"   Reason: {data['trigger_reason']}")
            print(f"   Price: ${data['metrics']['price_usd']}/MWh | Load: {data['metrics']['load_mw']} MW")

            if not SIMULATION_MODE:
                stop_mining_rigs()
            else:
                print("   [SIMULATION] Shutdown command would fire here.")

        else:
            print(f"\n[{timestamp}] 🟢 Grid Normal. Operations Nominal.")
            print(f"   Price: ${data['metrics']['price_usd']}/MWh | Utilization: {data['metrics']['utilization_pct']}%")

    except Exception as e:
        print(f"\nError connecting to GridWatch: {e}")

if __name__ == "__main__":
    print(f"--- GridWatch 'Kill Switch' Monitor Started ---")
    print(f"Monitoring: {REGION}")
    print(f"Thresholds: Price > ${PRICE_CAP} | Stress > {STRESS_CAP}%")
    print(f"Press Ctrl+C to stop.\n")

    while True:
        check_grid_status()
        # Check every 5 minutes (300 seconds)
        time.sleep(300)
