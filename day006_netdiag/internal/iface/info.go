package iface

import (
	"fmt"
	"net"
)

type Interface struct {
	Name      string
	HardwareAddr string
	Flags     []string
	Addresses []Address
}

type Address struct {
	IP      string
	Network string
	IsIPv6  bool
}

func List() ([]Interface, error) {
	ifaces, err := net.Interfaces()
	if err != nil {
		return nil, fmt.Errorf("failed to list interfaces: %w", err)
	}

	var result []Interface
	for _, iface := range ifaces {
		info := Interface{
			Name:         iface.Name,
			HardwareAddr: iface.HardwareAddr.String(),
			Flags:        parseFlags(iface.Flags),
		}

		addrs, err := iface.Addrs()
		if err != nil {
			continue
		}

		for _, addr := range addrs {
			ip, network, err := net.ParseCIDR(addr.String())
			if err != nil {
				continue
			}
			info.Addresses = append(info.Addresses, Address{
				IP:      ip.String(),
				Network: network.String(),
				IsIPv6:  ip.To4() == nil,
			})
		}

		result = append(result, info)
	}
	return result, nil
}

func parseFlags(flags net.Flags) []string {
	var result []string
	flagMap := map[net.Flags]string{
		net.FlagUp:           "UP",
		net.FlagBroadcast:    "BROADCAST",
		net.FlagLoopback:     "LOOPBACK",
		net.FlagPointToPoint: "P2P",
		net.FlagMulticast:    "MULTICAST",
	}
	for flag, name := range flagMap {
		if flags&flag != 0 {
			result = append(result, name)
		}
	}
	return result
}
