package main

import (
	"flag"
	"fmt"
	"net"
	"os"
	"strings"
)

var (
	homeIP  string
	port    int
	operSys string
)

func init() {
	flag.StringVar(&homeIP, "home", "", "home/your ip")
	flag.IntVar(&port, "p", 0, "dest port to callback")
	flag.StringVar(&operSys, "o", "", "victim operating system")
	flag.Parse()

	validateAgrs()

}

func main() {

}

func isValidOS(osName string) bool {
	switch strings.ToLower(osName) {
	case "linux":
		return true
	case "mac":
		return true
	case "win":
		return true
	default:
		return false
	}

}

func validateAgrs() {

	if !argExists(homeIP, port, operSys) {
		fmt.Println("flag cannot be empty")
		os.Exit(0)
	}

	x := net.ParseIP(homeIP)

	if x == nil {
		fmt.Println("invalid ip address: ", homeIP)
		os.Exit(0)
	}

	if port <= 1024 || port >= 65535 {
		fmt.Println("invalid port")
	}

	if !isValidOS(operSys) {
		fmt.Println("invalid os")
	}
}

func argExists(args ...any) bool {

	for _, arg := range args {
		switch v := arg.(type) {
		case int:
			if v == 0 {
				return false
			}
		case string:
			if v == "" {
				return false
			}
		}
	}

	return true

}
