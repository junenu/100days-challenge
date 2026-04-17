package subnet

import (
	"testing"
)

func TestCalculate(t *testing.T) {
	tests := []struct {
		cidr        string
		wantNetwork string
		wantMask    string
		wantBcast   string
		wantFirst   string
		wantLast    string
		wantTotal   uint64
		wantUsable  uint64
		wantClass   string
		wantAddrType AddressType
	}{
		{
			cidr:         "192.168.1.0/24",
			wantNetwork:  "192.168.1.0/24",
			wantMask:     "255.255.255.0",
			wantBcast:    "192.168.1.255",
			wantFirst:    "192.168.1.1",
			wantLast:     "192.168.1.254",
			wantTotal:    256,
			wantUsable:   254,
			wantClass:    "C",
			wantAddrType: AddressTypeRFC1918,
		},
		{
			cidr:         "10.0.0.0/8",
			wantNetwork:  "10.0.0.0/8",
			wantMask:     "255.0.0.0",
			wantBcast:    "10.255.255.255",
			wantFirst:    "10.0.0.1",
			wantLast:     "10.255.255.254",
			wantTotal:    16777216,
			wantUsable:   16777214,
			wantClass:    "A",
			wantAddrType: AddressTypeRFC1918,
		},
		{
			cidr:         "172.16.0.0/12",
			wantNetwork:  "172.16.0.0/12",
			wantMask:     "255.240.0.0",
			wantBcast:    "172.31.255.255",
			wantFirst:    "172.16.0.1",
			wantLast:     "172.31.255.254",
			wantTotal:    1048576,
			wantUsable:   1048574,
			wantClass:    "B",
			wantAddrType: AddressTypeRFC1918,
		},
		{
			cidr:         "8.8.8.0/24",
			wantNetwork:  "8.8.8.0/24",
			wantMask:     "255.255.255.0",
			wantBcast:    "8.8.8.255",
			wantFirst:    "8.8.8.1",
			wantLast:     "8.8.8.254",
			wantTotal:    256,
			wantUsable:   254,
			wantClass:    "A",
			wantAddrType: AddressTypePublic,
		},
		{
			cidr:         "192.168.1.100/30",
			wantNetwork:  "192.168.1.100/30",
			wantMask:     "255.255.255.252",
			wantBcast:    "192.168.1.103",
			wantFirst:    "192.168.1.101",
			wantLast:     "192.168.1.102",
			wantTotal:    4,
			wantUsable:   2,
			wantClass:    "C",
			wantAddrType: AddressTypeRFC1918,
		},
		{
			// /32: ホスト 1 台、ネットワーク・ブロードキャスト区別なし
			cidr:         "192.168.1.0/32",
			wantNetwork:  "192.168.1.0/32",
			wantMask:     "255.255.255.255",
			wantBcast:    "192.168.1.0",
			wantFirst:    "192.168.1.0",
			wantLast:     "192.168.1.0",
			wantTotal:    1,
			wantUsable:   1,
			wantClass:    "C",
			wantAddrType: AddressTypeRFC1918,
		},
		{
			// /31: P2P リンク用 (RFC3021)。2 ホスト、usable も 2
			cidr:         "192.168.1.0/31",
			wantNetwork:  "192.168.1.0/31",
			wantMask:     "255.255.255.254",
			wantBcast:    "192.168.1.1",
			wantFirst:    "192.168.1.0",
			wantLast:     "192.168.1.1",
			wantTotal:    2,
			wantUsable:   2,
			wantClass:    "C",
			wantAddrType: AddressTypeRFC1918,
		},
	}

	for _, tt := range tests {
		t.Run(tt.cidr, func(t *testing.T) {
			info, err := Calculate(tt.cidr)
			if err != nil {
				t.Fatalf("Calculate(%q) error: %v", tt.cidr, err)
			}

			if info.Network != tt.wantNetwork {
				t.Errorf("Network = %q, want %q", info.Network, tt.wantNetwork)
			}
			if info.Mask != tt.wantMask {
				t.Errorf("Mask = %q, want %q", info.Mask, tt.wantMask)
			}
			if info.Broadcast != tt.wantBcast {
				t.Errorf("Broadcast = %q, want %q", info.Broadcast, tt.wantBcast)
			}
			if info.FirstHost != tt.wantFirst {
				t.Errorf("FirstHost = %q, want %q", info.FirstHost, tt.wantFirst)
			}
			if info.LastHost != tt.wantLast {
				t.Errorf("LastHost = %q, want %q", info.LastHost, tt.wantLast)
			}
			if info.TotalHosts != tt.wantTotal {
				t.Errorf("TotalHosts = %d, want %d", info.TotalHosts, tt.wantTotal)
			}
			if info.UsableHosts != tt.wantUsable {
				t.Errorf("UsableHosts = %d, want %d", info.UsableHosts, tt.wantUsable)
			}
			if info.Class != tt.wantClass {
				t.Errorf("Class = %q, want %q", info.Class, tt.wantClass)
			}
			if info.AddrType != tt.wantAddrType {
				t.Errorf("AddrType = %q, want %q", info.AddrType, tt.wantAddrType)
			}
		})
	}
}

func TestCalculate_InvalidCIDR(t *testing.T) {
	_, err := Calculate("not-a-cidr")
	if err == nil {
		t.Error("expected error for invalid CIDR, got nil")
	}
}

func TestCalculate_IPv6Rejected(t *testing.T) {
	_, err := Calculate("2001:db8::/32")
	if err == nil {
		t.Error("expected error for IPv6 CIDR, got nil")
	}
}

func TestClassOf(t *testing.T) {
	tests := []struct {
		cidr  string
		class string
	}{
		{"1.0.0.0/8", "A"},
		{"127.0.0.0/8", "A"},
		{"128.0.0.0/16", "B"},
		{"191.255.0.0/16", "B"},
		{"192.0.0.0/24", "C"},
		{"223.255.255.0/24", "C"},
		{"224.0.0.0/4", "D (Multicast)"},
		{"240.0.0.0/4", "E (Reserved)"},
	}

	for _, tt := range tests {
		t.Run(tt.cidr, func(t *testing.T) {
			info, err := Calculate(tt.cidr)
			if err != nil {
				t.Fatalf("Calculate(%q) error: %v", tt.cidr, err)
			}
			if info.Class != tt.class {
				t.Errorf("Class = %q, want %q", info.Class, tt.class)
			}
		})
	}
}

func TestAddrType(t *testing.T) {
	tests := []struct {
		cidr     string
		addrType AddressType
	}{
		{"10.0.0.0/8", AddressTypeRFC1918},
		{"172.16.0.0/12", AddressTypeRFC1918},
		{"192.168.0.0/16", AddressTypeRFC1918},
		{"127.0.0.0/8", AddressTypeLoopback},
		{"169.254.0.0/16", AddressTypeLinkLocal},
		{"8.8.8.0/24", AddressTypePublic},
	}

	for _, tt := range tests {
		t.Run(tt.cidr, func(t *testing.T) {
			info, err := Calculate(tt.cidr)
			if err != nil {
				t.Fatalf("Calculate(%q) error: %v", tt.cidr, err)
			}
			if info.AddrType != tt.addrType {
				t.Errorf("AddrType = %q, want %q", info.AddrType, tt.addrType)
			}
		})
	}
}
