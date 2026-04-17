package scanner

import (
	"fmt"
	"net"
	"sort"
	"sync"
	"time"
)

type PortState string

const (
	StateOpen   PortState = "open"
	StateClosed PortState = "closed"
)

type PortResult struct {
	Port    int
	State   PortState
	Service string
}

type ScanResult struct {
	Host    string
	IP      string
	Ports   []PortResult
	Elapsed time.Duration
}

var commonServices = map[int]string{
	21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
	80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
	3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 6379: "Redis",
	8080: "HTTP-alt", 8443: "HTTPS-alt", 27017: "MongoDB",
	161: "SNMP", 162: "SNMP-trap", 179: "BGP", 520: "RIP",
	1194: "OpenVPN", 1723: "PPTP", 4500: "IPSec-NAT", 500: "IKE",
}

func Scan(host string, ports []int, concurrency int, timeout time.Duration) (*ScanResult, error) {
	ips, err := net.LookupHost(host)
	if err != nil {
		return nil, fmt.Errorf("host resolution failed: %w", err)
	}

	ip := ips[0]
	start := time.Now()
	result := &ScanResult{Host: host, IP: ip}

	sem := make(chan struct{}, concurrency)
	var mu sync.Mutex
	var wg sync.WaitGroup

	for _, port := range ports {
		wg.Add(1)
		go func(p int) {
			defer wg.Done()
			sem <- struct{}{}
			defer func() { <-sem }()

			state := probe(ip, p, timeout)
			if state == StateOpen {
				mu.Lock()
				result.Ports = append(result.Ports, PortResult{
					Port:    p,
					State:   state,
					Service: serviceOf(p),
				})
				mu.Unlock()
			}
		}(port)
	}

	wg.Wait()
	sort.Slice(result.Ports, func(i, j int) bool {
		return result.Ports[i].Port < result.Ports[j].Port
	})
	result.Elapsed = time.Since(start)
	return result, nil
}

func probe(ip string, port int, timeout time.Duration) PortState {
	addr := fmt.Sprintf("%s:%d", ip, port)
	conn, err := net.DialTimeout("tcp", addr, timeout)
	if err != nil {
		return StateClosed
	}
	conn.Close()
	return StateOpen
}

func serviceOf(port int) string {
	if svc, ok := commonServices[port]; ok {
		return svc
	}
	return "unknown"
}

func ParsePortRange(rangeStr string) ([]int, error) {
	var start, end int
	n, err := fmt.Sscanf(rangeStr, "%d-%d", &start, &end)
	if n == 2 && err == nil {
		if start < 1 || end > 65535 || start > end {
			return nil, fmt.Errorf("invalid port range: %s", rangeStr)
		}
		ports := make([]int, end-start+1)
		for i := range ports {
			ports[i] = start + i
		}
		return ports, nil
	}

	var port int
	if _, err := fmt.Sscanf(rangeStr, "%d", &port); err != nil {
		return nil, fmt.Errorf("invalid port: %s", rangeStr)
	}
	return []int{port}, nil
}

func CommonPorts() []int {
	ports := make([]int, 0, len(commonServices))
	for p := range commonServices {
		ports = append(ports, p)
	}
	sort.Ints(ports)
	return ports
}
