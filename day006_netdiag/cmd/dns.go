package cmd

import (
	"fmt"
	"os"
	"strings"

	"github.com/junenu/netdiag/internal/dns"
	"github.com/olekukonko/tablewriter"
	"github.com/spf13/cobra"
)

var (
	dnsTypes   []string
	dnsReverse bool
)

var dnsCmd = &cobra.Command{
	Use:   "dns <domain|IP>",
	Short: "DNS レコード検索",
	Example: `  netdiag dns example.com
  netdiag dns example.com --type A,MX,TXT
  netdiag dns 8.8.8.8 --reverse`,
	Args: cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		target := args[0]

		var result *dns.Result
		var err error

		if dnsReverse {
			fmt.Printf("\n[ Reverse DNS Lookup: %s ]\n\n", target)
			result, err = dns.LookupReverse(target)
		} else {
			types := expandTypes(dnsTypes)
			fmt.Printf("\n[ DNS Lookup: %s ]\n\n", target)
			result, err = dns.Lookup(target, types)
		}

		if err != nil {
			return err
		}

		if len(result.Records) == 0 {
			fmt.Println("No records found.")
			return nil
		}

		table := tablewriter.NewWriter(os.Stdout)
		table.Header([]string{"Type", "Value"})

		for _, r := range result.Records {
			table.Append([]string{string(r.Type), r.Value})
		}
		table.Render()

		fmt.Printf("\nQuery time: %s\n\n", result.Elapsed.Round(1000000))
		return nil
	},
}

func expandTypes(types []string) []string {
	var result []string
	for _, t := range types {
		for _, s := range strings.Split(t, ",") {
			s = strings.TrimSpace(s)
			if s != "" {
				result = append(result, s)
			}
		}
	}
	return result
}

func init() {
	dnsCmd.Flags().StringSliceVar(&dnsTypes, "type", nil, "レコードタイプ (A,AAAA,MX,NS,TXT,CNAME)")
	dnsCmd.Flags().BoolVar(&dnsReverse, "reverse", false, "逆引き DNS (PTR)")
}
