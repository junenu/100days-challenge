package subnet

import (
	"fmt"
	"math"
	"net"
)

type Info struct {
	Network     string
	Mask        string
	MaskBits    int
	Broadcast   string
	FirstHost   string
	LastHost    string
	TotalHosts  uint64
	UsableHosts uint64
	NetworkAddr net.IP
	Class       string
	IsPrivate   bool
}

func Calculate(cidr string) (*Info, error) {
	ip, network, err := net.ParseCIDR(cidr)
	if err != nil {
		return nil, fmt.Errorf("invalid CIDR: %w", err)
	}

	ones, bits := network.Mask.Size()
	totalHosts := uint64(math.Pow(2, float64(bits-ones)))
	usableHosts := totalHosts
	if ones < bits {
		usableHosts = totalHosts - 2
	}

	broadcast := make(net.IP, len(network.IP))
	for i := range network.IP {
		broadcast[i] = network.IP[i] | ^network.Mask[i]
	}

	firstHost := make(net.IP, len(network.IP))
	copy(firstHost, network.IP)
	if ones < bits {
		firstHost[len(firstHost)-1]++
	}

	lastHost := make(net.IP, len(broadcast))
	copy(lastHost, broadcast)
	if ones < bits {
		lastHost[len(lastHost)-1]--
	}

	return &Info{
		Network:     network.String(),
		Mask:        fmt.Sprintf("%d.%d.%d.%d", network.Mask[0], network.Mask[1], network.Mask[2], network.Mask[3]),
		MaskBits:    ones,
		Broadcast:   broadcast.String(),
		FirstHost:   firstHost.String(),
		LastHost:    lastHost.String(),
		TotalHosts:  totalHosts,
		UsableHosts: usableHosts,
		NetworkAddr: network.IP,
		Class:       classOf(ip),
		IsPrivate:   isPrivate(ip),
	}, nil
}

func classOf(ip net.IP) string {
	ip = ip.To4()
	if ip == nil {
		return "IPv6"
	}
	switch {
	case ip[0] < 128:
		return "A"
	case ip[0] < 192:
		return "B"
	case ip[0] < 224:
		return "C"
	case ip[0] < 240:
		return "D (Multicast)"
	default:
		return "E (Reserved)"
	}
}

var privateRanges = []string{
	"10.0.0.0/8",
	"172.16.0.0/12",
	"192.168.0.0/16",
	"127.0.0.0/8",
	"169.254.0.0/16",
}

func isPrivate(ip net.IP) bool {
	for _, cidr := range privateRanges {
		_, network, _ := net.ParseCIDR(cidr)
		if network.Contains(ip) {
			return true
		}
	}
	return false
}
