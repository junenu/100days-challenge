package scanner

import (
	"fmt"
	"net"
	"sort"
	"strconv"
	"strings"
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
	if concurrency < 1 {
		return nil, fmt.Errorf("concurrency must be >= 1, got %d", concurrency)
	}

	ips, err := net.LookupHost(host)
	if err != nil {
		return nil, fmt.Errorf("host resolution failed: %w", err)
	}

	ip := ips[0]
	start := time.Now()
	result := &ScanResult{Host: host, IP: ip}

	// worker pool: concurrency 数の worker を固定して順にポートを処理する
	jobs := make(chan int, len(ports))
	for _, p := range ports {
		jobs <- p
	}
	close(jobs)

	var mu sync.Mutex
	var wg sync.WaitGroup

	for i := 0; i < concurrency; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for p := range jobs {
				if probe(ip, p, timeout) == StateOpen {
					mu.Lock()
					result.Ports = append(result.Ports, PortResult{
						Port:    p,
						State:   StateOpen,
						Service: serviceOf(p),
					})
					mu.Unlock()
				}
			}
		}()
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
	// 範囲指定: "1-1024"
	if strings.Contains(rangeStr, "-") {
		parts := strings.SplitN(rangeStr, "-", 2)
		start, err1 := parsePort(parts[0])
		end, err2 := parsePort(parts[1])
		if err1 != nil || err2 != nil || start > end {
			return nil, fmt.Errorf("invalid port range: %s", rangeStr)
		}
		ports := make([]int, end-start+1)
		for i := range ports {
			ports[i] = start + i
		}
		return ports, nil
	}

	// 単一ポート: "80"
	port, err := parsePort(rangeStr)
	if err != nil {
		return nil, err
	}
	return []int{port}, nil
}

func parsePort(s string) (int, error) {
	s = strings.TrimSpace(s)
	port, err := strconv.Atoi(s)
	if err != nil || port < 1 || port > 65535 {
		return 0, fmt.Errorf("invalid port: %s (must be 1-65535)", s)
	}
	return port, nil
}

func CommonPorts() []int {
	ports := make([]int, 0, len(commonServices))
	for p := range commonServices {
		ports = append(ports, p)
	}
	sort.Ints(ports)
	return ports
}
