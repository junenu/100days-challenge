package cmd

import (
	"fmt"
	"os"

	"github.com/junenu/netdiag/internal/subnet"
	"github.com/olekukonko/tablewriter"
	"github.com/spf13/cobra"
)

var subnetCmd = &cobra.Command{
	Use:   "subnet <CIDR>",
	Short: "CIDR サブネット計算",
	Example: `  netdiag subnet 192.168.1.0/24
  netdiag subnet 10.0.0.0/8
  netdiag subnet 172.16.0.0/12`,
	Args: cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		info, err := subnet.Calculate(args[0])
		if err != nil {
			return err
		}

		fmt.Printf("\n[ Subnet Calculator: %s ]\n\n", args[0])

		table := tablewriter.NewWriter(os.Stdout)

		rows := [][]string{
			{"Network Address", info.Network},
			{"Subnet Mask", fmt.Sprintf("%s (/%d)", info.Mask, info.MaskBits)},
			{"Broadcast Address", info.Broadcast},
			{"First Host", info.FirstHost},
			{"Last Host", info.LastHost},
			{"Total Hosts", fmt.Sprintf("%d", info.TotalHosts)},
			{"Usable Hosts", fmt.Sprintf("%d", info.UsableHosts)},
			{"IP Class", info.Class},
			{"Address Type", string(info.AddrType)},
		}

		for _, row := range rows {
			table.Append(row)
		}
		table.Render()
		fmt.Println()
		return nil
	},
}
