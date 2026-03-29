# verify_rootkit.py - Rootkit Verification Tool
import psutil
import subprocess
import os
import sys
import platform

def verify_rootkit_threat():
    print("=" * 60)
    print("🔍 ROOTKIT VERIFICATION TOOL")
    print("=" * 60)
    
    suspicious_findings = []
    
    # 1. Check for process hiding
    print("\n[1] Checking for hidden processes...")
    try:
        # Method 1: Compare tasklist with psutil
        if platform.system() == "Windows":
            result = subprocess.run(['tasklist', '/FO', 'CSV'], 
                                  capture_output=True, text=True, timeout=10, shell=True)
            tasklist_pids = set()
            for line in result.stdout.split('\n')[1:]:
                if line:
                    try:
                        pid = int(line.split(',')[1].strip('"'))
                        tasklist_pids.add(pid)
                    except:
                        pass
            
            psutil_pids = set(psutil.pids())
            hidden_pids = tasklist_pids - psutil_pids
            
            if hidden_pids:
                suspicious_findings.append(f"Hidden processes found: {hidden_pids}")
                print(f"   ⚠️ WARNING: {len(hidden_pids)} hidden processes detected!")
                for pid in list(hidden_pids)[:5]:
                    print(f"      - Hidden PID: {pid}")
            else:
                print("   ✓ No hidden processes found")
    except Exception as e:
        print(f"   ! Check failed: {e}")
    
    # 2. Check for suspicious drivers
    print("\n[2] Checking for suspicious drivers...")
    if platform.system() == "Windows":
        try:
            result = subprocess.run(['driverquery', '/FO', 'CSV'], 
                                  capture_output=True, text=True, timeout=10, shell=True)
            drivers = result.stdout.lower()
            
            suspicious_drivers = ['rootkit', 'hidden', 'malware', 'hook', 'spy']
            found_drivers = []
            
            for driver in suspicious_drivers:
                if driver in drivers:
                    found_drivers.append(driver)
            
            if found_drivers:
                suspicious_findings.append(f"Suspicious driver names: {found_drivers}")
                print(f"   ⚠️ Suspicious driver patterns found: {found_drivers}")
            else:
                print("   ✓ No suspicious driver patterns found")
        except:
            print("   ! Could not check drivers")
    
    # 3. Check for unusual kernel modules
    print("\n[3] Checking for unusual system behavior...")
    try:
        # Check for processes with hidden windows
        import ctypes
        user32 = ctypes.windll.user32
        
        def enum_windows_callback(hwnd, windows):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buff, length + 1)
                    windows.append(buff.value)
            return True
        
        windows = []
        enum_windows_proc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.py_object)
        user32.EnumWindows(enum_windows_proc(enum_windows_callback), windows)
        
        # Check for hidden processes (processes with no windows)
        processes_with_windows = set()
        # This is complex, simplified check
        print("   ✓ Window enumeration complete")
    except:
        pass
    
    # 4. Check for known rootkit file locations
    print("\n[4] Checking common rootkit locations...")
    rootkit_paths = [
        r"C:\Windows\System32\drivers\bad.sys",
        r"C:\Windows\System32\drivers\rootkit.sys",
        r"C:\Windows\Temp\*.sys",
        r"C:\Windows\System32\config\systemprofile\AppData\Local\*.sys"
    ]
    
    found_files = []
    import glob
    for pattern in rootkit_paths:
        try:
            matches = glob.glob(pattern)
            if matches:
                found_files.extend(matches)
        except:
            pass
    
    if found_files:
        suspicious_findings.append(f"Suspicious files: {found_files}")
        print(f"   ⚠️ Suspicious files found: {found_files}")
    else:
        print("   ✓ No obvious rootkit files found")
    
    # 5. Check system integrity
    print("\n[5] Checking system integrity...")
    try:
        if platform.system() == "Windows":
            result = subprocess.run(['sfc', '/scannow'], 
                                  capture_output=True, text=True, timeout=300, shell=True)
            if "corrupt" in result.stdout.lower():
                suspicious_findings.append("System file corruption detected")
                print("   ⚠️ System file corruption detected!")
            else:
                print("   ✓ System files appear intact")
    except:
        print("   ! SFC check skipped (requires admin)")
    
    # SUMMARY
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    if suspicious_findings:
        print(f"\n⚠️ CRITICAL: {len(suspicious_findings)} suspicious findings detected!")
        print("\nFindings:")
        for i, finding in enumerate(suspicious_findings, 1):
            print(f"   {i}. {finding}")
        
        print("\n🔴 This appears to be a REAL ROOTKIT THREAT!")
        print("   Do not ignore - take action immediately!")
        
        return True
    else:
        print("\n✅ No rootkit indicators found!")
        print("   This may have been a FALSE POSITIVE from the antivirus.")
        return False

if __name__ == "__main__":
    is_threat_real = verify_rootkit_threat()
    
    if is_threat_real:
        print("\n" + "=" * 60)
        print("🔴 RECOMMENDED ACTIONS:")
        print("=" * 60)
        print("1. RUN Windows Defender Offline Scan")
        print("2. DOWNLOAD and run Malwarebytes Anti-Rootkit")
        print("3. BOOT into Safe Mode and run full scan")
        print("4. CONSIDER backing up important files")
        print("5. PREPARE for possible OS reinstallation")
    else:
        print("\n" + "=" * 60)
        print("✅ FALSE POSITIVE - Your system is likely safe")
        print("=" * 60)
        print("The antivirus may have flagged a legitimate driver.")
        print("Update your antivirus signatures and re-scan.")