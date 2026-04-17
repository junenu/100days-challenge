package scanner

import (
	"testing"
)

func TestParsePortRange(t *testing.T) {
	tests := []struct {
		input   string
		want    []int
		wantErr bool
	}{
		{"80", []int{80}, false},
		{"1-5", []int{1, 2, 3, 4, 5}, false},
		{"443-445", []int{443, 444, 445}, false},
		{"0-1", nil, true},
		{"1-65536", nil, true},
		{"100-50", nil, true},
		{"abc", nil, true},
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

func TestScan_Localhost(t *testing.T) {
	result, err := Scan("127.0.0.1", []int{65500, 65501, 65502}, 10, 100*1000*1000)
	if err != nil {
		t.Fatalf("Scan error: %v", err)
	}
	if result.IP == "" {
		t.Error("expected non-empty IP")
	}
	if result.Elapsed <= 0 {
		t.Error("expected positive elapsed time")
	}
}
