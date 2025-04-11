import time
from datetime import datetime

print("Starting dummy training...")
time.sleep(2)

with open("/app/train_output.txt", "w") as f:
    f.write(f"Training completed at {datetime.now()}\n")

print("Dummy training done! Output written to train_output.txt")
