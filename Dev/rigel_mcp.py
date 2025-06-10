from mcp.server.fastmcp import FastMCP
import os
import mimetypes
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
def open_file(file_path: str, line_number: int = None) -> str:
    try:
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' does not exist"
        
        file_size = os.path.getsize(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        file_extension = os.path.splitext(file_path)[1].lower()
        
        language_map = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
            '.html': 'html', '.css': 'css', '.json': 'json',
            '.md': 'markdown', '.txt': 'text', '.sh': 'bash',
            '.yml': 'yaml', '.yaml': 'yaml', '.xml': 'xml',
            '.sql': 'sql', '.cpp': 'cpp', '.c': 'c', '.java': 'java'
        }
        
        language = language_map.get(file_extension, 'text')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            return f"Error: Cannot read '{file_path}' - binary file or encoding issue"
        
        result = f"📁 {os.path.basename(file_path)} ({language})\n"
        result += f"📍 {file_path}\n"
        result += f"📊 {len(lines)} lines, {file_size} bytes\n"
        result += "─" * 50 + "\n"
        
        max_lines = min(100, len(lines))
        line_num_width = len(str(max_lines))
        
        for i, line in enumerate(lines[:max_lines], 1):
            line_prefix = f"{i:>{line_num_width}} │ "
            if line_number and i == line_number:
                result += f"➤ {line_prefix}{line.rstrip()}\n"
            else:
                result += f"  {line_prefix}{line.rstrip()}\n"
        
        if len(lines) > 100:
            result += f"\n... ({len(lines) - 100} more lines)\n"
        result += "─" * 50 + "\n"
        if line_number and line_number <= len(lines):
            result += f"🎯 Focused on line {line_number}\n"
        
        return result
        
    except PermissionError:
        return f"Error: Permission denied accessing '{file_path}'"
    except Exception as e:
        return f"Error opening file '{file_path}': {str(e)}"
    
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
