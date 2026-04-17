package cmd

import (
	"fmt"
	"os"
	"strings"
	"time"

	"github.com/junenu/netdiag/internal/scanner"
	"github.com/olekukonko/tablewriter"
	"github.com/spf13/cobra"
)

var (
	scanPorts       string
	scanConcurrency int
	scanTimeout     int
	scanCommon      bool
)

var scanCmd = &cobra.Command{
	Use:   "scan <host>",
	Short: "TCP ポートスキャン",
	Example: `  netdiag scan 192.168.1.1
  netdiag scan example.com --ports 1-1024
  netdiag scan 10.0.0.1 --ports 22,80,443,3306
  netdiag scan 192.168.1.1 --common`,
	Args: cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		host := args[0]
		timeout := time.Duration(scanTimeout) * time.Millisecond

		if scanConcurrency < 1 {
			return fmt.Errorf("--concurrency must be >= 1, got %d", scanConcurrency)
		}
		if scanTimeout < 1 {
			return fmt.Errorf("--timeout must be >= 1ms, got %d", scanTimeout)
		}

		var ports []int
		if scanCommon {
			ports = scanner.CommonPorts()
		} else if scanPorts != "" {
			for _, part := range strings.Split(scanPorts, ",") {
				part = strings.TrimSpace(part)
				p, err := scanner.ParsePortRange(part)
				if err != nil {
					return fmt.Errorf("invalid port specification '%s': %w", part, err)
				}
				ports = append(ports, p...)
			}
		} else {
			ports = scanner.CommonPorts()
		}

		fmt.Printf("\n[ Port Scan: %s ]\n", host)
		fmt.Printf("Scanning %d ports (concurrency: %d, timeout: %dms)...\n\n",
			len(ports), scanConcurrency, scanTimeout)

		result, err := scanner.Scan(host, ports, scanConcurrency, timeout)
		if err != nil {
			return err
		}

		fmt.Printf("Target IP: %s\n\n", result.IP)

		if len(result.Ports) == 0 {
			fmt.Println("No open ports found.")
		} else {
			table := tablewriter.NewWriter(os.Stdout)
			table.Header([]string{"Port", "State", "Service"})

			for _, p := range result.Ports {
				table.Append([]string{
					fmt.Sprintf("%d", p.Port),
					string(p.State),
					p.Service,
				})
			}
			table.Render()
			fmt.Printf("\n%d open port(s) found.\n", len(result.Ports))
		}

		fmt.Printf("Scan completed in %s\n\n", result.Elapsed.Round(time.Millisecond))
		return nil
	},
}

func init() {
	scanCmd.Flags().StringVar(&scanPorts, "ports", "", "スキャン対象ポート (例: 22,80,443 または 1-1024)")
	scanCmd.Flags().BoolVar(&scanCommon, "common", false, "一般的なポートをスキャン")
	scanCmd.Flags().IntVar(&scanConcurrency, "concurrency", 100, "並列スキャン数")
	scanCmd.Flags().IntVar(&scanTimeout, "timeout", 500, "接続タイムアウト (ms)")
}
