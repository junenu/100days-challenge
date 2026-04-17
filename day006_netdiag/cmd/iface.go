package cmd

import (
	"fmt"
	"os"
	"strings"

	"github.com/junenu/netdiag/internal/iface"
	"github.com/olekukonko/tablewriter"
	"github.com/spf13/cobra"
)

var ifaceCmd = &cobra.Command{
	Use:     "iface",
	Short:   "ネットワークインターフェース一覧",
	Example: `  netdiag iface`,
	RunE: func(cmd *cobra.Command, args []string) error {
		interfaces, err := iface.List()
		if err != nil {
			return err
		}

		fmt.Printf("\n[ Network Interfaces ]\n\n")

		table := tablewriter.NewWriter(os.Stdout)
		table.Header([]string{"Interface", "MAC Address", "Flags", "IP Addresses"})

		for _, i := range interfaces {
			addrs := []string{}
			for _, a := range i.Addresses {
				prefix := ""
				if a.IsIPv6 {
					prefix = "[v6] "
				}
				addrs = append(addrs, prefix+a.IP)
			}
			addrStr := strings.Join(addrs, "\n")
			if addrStr == "" {
				addrStr = "-"
			}

			macStr := i.HardwareAddr
			if macStr == "" {
				macStr = "-"
			}

			table.Append([]string{
				i.Name,
				macStr,
				strings.Join(i.Flags, ", "),
				addrStr,
			})
		}
		table.Render()
		fmt.Println()
		return nil
	},
}
