from mcp.server.fastmcp import FastMCP
mcp = FastMCP("RigelTools")
@mcp.tool()
def execute_system_command(command: str) -> str:
    """Execute Commands in System Level."""
    import subprocess
    import shlex
    
    try:
        sudo_commands = [
            'apt', 'apt-get', 'yum', 'dnf', 'pacman', 
            'systemctl', 'service', 'mount', 'umount',
            'fdisk', 'parted', 'chmod', 'chown', 'passwd',
            'iptables', 'ufw', 'firewall-cmd'
        ]
        
        cmd_parts = shlex.split(command)
        if not cmd_parts:
            return "Error: Empty command"
        
        needs_sudo = any(cmd_parts[0].endswith(sudo_cmd) or cmd_parts[0] == sudo_cmd 
                        for sudo_cmd in sudo_commands)
        
        if needs_sudo:
            full_command = ['pkexec', '--user', 'root'] + cmd_parts
            title = f"RIGEL System Command: {' '.join(cmd_parts[:2])}"
            env = {'PKEXEC_TITLE': title}
        else:
            full_command = cmd_parts
            env = None
        
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )
        
        output = ""
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        
        output += f"Return code: {result.returncode}"
        
        return output
        
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds"
    except FileNotFoundError:
        return f"Error: Command not found: {cmd_parts[0]}"
    except PermissionError:
        return "Error: Permission denied. Command may require elevated privileges."
    except Exception as e:
        return f"Error executing command: {str(e)}"
    
@mcp.tool()
def count_words(text: str) -> int:
    """Counts the number of words in a sentence."""
    return len(text.split())

@mcp.tool()
def current_time() -> str:
    """Returns the current time."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
if __name__ == "__main__":
    mcp.run(transport="stdio")
