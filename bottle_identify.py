import time
from bottle_identify import measure_distance, is_bottle_present

try:
    print("📡 Testing ultrasonic sensor... Press Ctrl+C to stop.")
    while True:
        distance = measure_distance()
        print(f"Distance: {distance} cm")

        if is_bottle_present():
            print("✅ Bottle detected (within threshold distance)")
        else:
            print("⏳ No bottle detected")

        time.sleep(1)

except KeyboardInterrupt:
    print("🛑 Test stopped by user")

finally:
    from bottle_identify import cleanup
    cleanup()
    print("🔌 GPIO cleaned up")
