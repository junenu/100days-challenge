package scanner

import (
	"net"
	"testing"
	"time"
)

func TestParsePortRange(t *testing.T) {
	tests := []struct {
		input   string
		want    []int
		wantErr bool
	}{
		{"80", []int{80}, false},
		{"1", []int{1}, false},
		{"65535", []int{65535}, false},
		{"1-5", []int{1, 2, 3, 4, 5}, false},
		{"443-445", []int{443, 444, 445}, false},
		// 異常系: 範囲指定
		{"0-1", nil, true},
		{"1-65536", nil, true},
		{"100-50", nil, true},
		// 異常系: 単一ポート
		{"0", nil, true},
		{"65536", nil, true},
		{"abc", nil, true},
		{"80abc", nil, true},
		{"", nil, true},
		{"-1", nil, true},
	}

	for _, tt := range tests {
		t.Run(tt.input, func(t *testing.T) {
			got, err := ParsePortRange(tt.input)
			if (err != nil) != tt.wantErr {
				t.Errorf("ParsePortRange(%q) error = %v, wantErr = %v", tt.input, err, tt.wantErr)
				return
			}
			if !tt.wantErr {
				if len(got) != len(tt.want) {
					t.Errorf("ParsePortRange(%q) = %v, want %v", tt.input, got, tt.want)
					return
				}
				for i := range got {
					if got[i] != tt.want[i] {
						t.Errorf("ParsePortRange(%q)[%d] = %d, want %d", tt.input, i, got[i], tt.want[i])
					}
				}
			}
		})
	}
}

func TestServiceOf(t *testing.T) {
	tests := []struct {
		port    int
		service string
	}{
		{22, "SSH"},
		{80, "HTTP"},
		{443, "HTTPS"},
		{3306, "MySQL"},
		{9999, "unknown"},
	}

	for _, tt := range tests {
		t.Run(tt.service, func(t *testing.T) {
			got := serviceOf(tt.port)
			if got != tt.service {
				t.Errorf("serviceOf(%d) = %q, want %q", tt.port, got, tt.service)
			}
		})
	}
}

func TestCommonPorts(t *testing.T) {
	ports := CommonPorts()
	if len(ports) == 0 {
		t.Error("CommonPorts() returned empty slice")
	}
	for i := 1; i < len(ports); i++ {
		if ports[i] <= ports[i-1] {
			t.Errorf("CommonPorts() not sorted at index %d: %d <= %d", i, ports[i], ports[i-1])
		}
	}
}

func TestScan_OpenAndClosed(t *testing.T) {
	// 一時 TCP サーバーを立てて open/closed 両方を検証する
	ln, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatalf("failed to listen: %v", err)
	}
	defer ln.Close()

	openPort := ln.Addr().(*net.TCPAddr).Port
	// 確実に閉じているポート (一時的に Listen してすぐ Close)
	ln2, _ := net.Listen("tcp", "127.0.0.1:0")
	closedPort := ln2.Addr().(*net.TCPAddr).Port
	ln2.Close()

	result, err := Scan("127.0.0.1", []int{openPort, closedPort}, 10, 500*time.Millisecond)
	if err != nil {
		t.Fatalf("Scan error: %v", err)
	}

	if len(result.Ports) != 1 {
		t.Fatalf("expected 1 open port, got %d: %v", len(result.Ports), result.Ports)
	}
	if result.Ports[0].Port != openPort {
		t.Errorf("expected open port %d, got %d", openPort, result.Ports[0].Port)
	}
}

func TestScan_InvalidConcurrency(t *testing.T) {
	_, err := Scan("127.0.0.1", []int{80}, 0, time.Second)
	if err == nil {
		t.Error("expected error for concurrency=0, got nil")
	}

	_, err = Scan("127.0.0.1", []int{80}, -1, time.Second)
	if err == nil {
		t.Error("expected error for concurrency=-1, got nil")
	}
}
