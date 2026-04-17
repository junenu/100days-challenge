package subnet

import (
	"fmt"
	"net"
)

// AddressType はアドレス空間の種別を表す。
type AddressType string

const (
	AddressTypePublic   AddressType = "Public"
	AddressTypeRFC1918  AddressType = "Private (RFC1918)"
	AddressTypeLoopback AddressType = "Loopback"
	AddressTypeLinkLocal AddressType = "Link-local"
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
	AddrType    AddressType
}

func Calculate(cidr string) (*Info, error) {
	ip, network, err := net.ParseCIDR(cidr)
	if err != nil {
		return nil, fmt.Errorf("invalid CIDR: %w", err)
	}

	if ip.To4() == nil {
		return nil, fmt.Errorf("IPv6 is not supported: %s", cidr)
	}

	ones, bits := network.Mask.Size()
	hostBits := bits - ones

	// /32 と /31 は特殊: ホスト数をそのまま使う
	totalHosts := uint64(1) << uint(hostBits)
	usableHosts := totalHosts
	if hostBits >= 2 {
		usableHosts = totalHosts - 2
	}

	broadcast := make(net.IP, len(network.IP))
	for i := range network.IP {
		broadcast[i] = network.IP[i] | ^network.Mask[i]
	}

	firstHost := make(net.IP, len(network.IP))
	copy(firstHost, network.IP)
	if hostBits >= 2 {
		firstHost[len(firstHost)-1]++
	}

	lastHost := make(net.IP, len(broadcast))
	copy(lastHost, broadcast)
	if hostBits >= 2 {
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
		AddrType:    addrTypeOf(ip),
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

type addrRange struct {
	cidr     string
	addrType AddressType
}

var addrRanges = []addrRange{
	{"127.0.0.0/8", AddressTypeLoopback},
	{"169.254.0.0/16", AddressTypeLinkLocal},
	{"10.0.0.0/8", AddressTypeRFC1918},
	{"172.16.0.0/12", AddressTypeRFC1918},
	{"192.168.0.0/16", AddressTypeRFC1918},
}

func addrTypeOf(ip net.IP) AddressType {
	for _, r := range addrRanges {
		_, network, _ := net.ParseCIDR(r.cidr)
		if network.Contains(ip) {
			return r.addrType
		}
	}
	return AddressTypePublic
}
