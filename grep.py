import subprocess
import time
import sys

def main():
    if len(sys.argv) < 3:
        print("Usage: python grep.py <pattern> <command>")
        sys.exit(1)

    pattern = sys.argv[1]
    command = sys.argv[2]
    args = sys.argv[3:]
    
    try:
        grep_command(pattern, command, args)
    except KeyboardInterrupt:
        print("\nReceived interrupt, shutting down...")
        sys.exit(0)

def grep_command(pattern, command, args):
    # Start the command
    print(f"Spawning command: {command} {' '.join(args)}")
    try:
        # Use Popen to capture output in real-time
        process = subprocess.Popen(
            [command] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Monitor the output
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                if pattern in output:
                    print(f"\nPattern '{pattern}' found! Terminating {command}.")
                    process.terminate()
                    try:
                        process.wait(timeout=5)  # Wait up to 5 seconds for graceful termination
                    except subprocess.TimeoutExpired:
                        print("Process didn't terminate gracefully, forcing...")
                        process.kill()
                    return True
        
        # Check if process ended normally
        return_code = process.poll()
        if return_code != 0:
            print(f"\nCommand exited with non-zero status: {return_code}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    main()
