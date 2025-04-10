import time
from full_container import measure_container_distance, is_container_full

try:
    print("🧪 Testing container fullness sensor... Press Ctrl+C to stop.")
    while True:
        distance = measure_container_distance()
        print(f"Container distance: {distance} cm")

        if is_container_full():
            print("🟥 Container is FULL")
        else:
            print("🟩 Container is NOT full")

        time.sleep(1)

except KeyboardInterrupt:
    print("🛑 Test stopped by user")

finally:
    from full_container import cleanup
    cleanup()
    print("🔌 GPIO cleaned up")
