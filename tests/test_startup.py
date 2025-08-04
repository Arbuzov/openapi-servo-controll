import subprocess
import sys

def test_app_starts():
    try:
        result = subprocess.run([
            sys.executable, '-m', 'openapi_servo_control'
        ], capture_output=True, timeout=10)
        assert result.returncode == 0, f"App failed to start: {result.stderr.decode()}"
    except Exception as e:
        assert False, f"Exception during app start: {e}"

if __name__ == "__main__":
    test_app_starts()
    print("App starts successfully.")
