import os
import sys

dwsim_path = os.getenv('DWSIM_PATH', 'C:\\Program Files\\DWSIM')
print(f"DWSIM Path: {dwsim_path}")

# Check if path exists
if os.path.exists(dwsim_path):
    print("✅ DWSIM directory exists")
    
    # List important files
    required_files = ['DWSIM.exe', 'DWSIM.Interfaces.dll']
    for file in required_files:
        file_path = os.path.join(dwsim_path, file)
        if os.path.exists(file_path):
            print(f"✅ {file} found")
        else:
            print(f"❌ {file} NOT found")
else:
    print("❌ DWSIM directory NOT found")
    print("Please check your DWSIM_PATH in .env file")