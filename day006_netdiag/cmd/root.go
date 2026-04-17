package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:   "netdiag",
	Short: "Network diagnostic toolkit for engineers",
	Long: `netdiag - ネットワークエンジニアのための診断ツール

コマンド一覧:
  subnet  サブネット計算 (CIDR → ブロードキャスト・ホスト範囲)
  dns     DNS レコード検索 (A/AAAA/MX/NS/TXT/CNAME/PTR)
  scan    TCP ポートスキャン
  iface   ネットワークインターフェース一覧`,
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func init() {
	rootCmd.AddCommand(subnetCmd)
	rootCmd.AddCommand(dnsCmd)
	rootCmd.AddCommand(scanCmd)
	rootCmd.AddCommand(ifaceCmd)
}
