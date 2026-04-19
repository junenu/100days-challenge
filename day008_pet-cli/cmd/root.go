package cmd

import (
	"fmt"
	"os"
	"time"

	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:   "pet",
	Short: "ターミナルに住む育成ペット",
	Long:  "ターミナルに住む小さなペットを育てよう。ご飯・遊び・休息で面倒を見てあげてね。",
	RunE: func(cmd *cobra.Command, args []string) error {
		return cmd.Help()
	},
}

var newCmd = &cobra.Command{
	Use:   "new <name>",
	Short: "新しいペットを迎える",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		existing, err := loadPet()
		if err != nil {
			return err
		}
		if existing != nil {
			fmt.Printf("すでに %s がいます！先に `pet goodbye` で別れを告げてね。\n", existing.Name)
			return nil
		}

		name := args[0]
		p := &Pet{
			Name:      name,
			Hunger:    70,
			Happiness: 70,
			Energy:    70,
			Age:       0,
			LastSeen:  time.Now(),
			BornAt:    time.Now(),
		}
		if err := savePet(p); err != nil {
			return err
		}
		fmt.Printf("\n🎉 %s がやってきた！\n", name)
		fmt.Println("  「はじめまして！よろしくね！」")
		fmt.Println()
		fmt.Println("コマンド一覧:")
		fmt.Println("  pet status   — 様子を見る")
		fmt.Println("  pet feed     — ごはんをあげる")
		fmt.Println("  pet play     — 一緒に遊ぶ")
		fmt.Println("  pet rest     — 休ませる")
		fmt.Println("  pet goodbye  — お別れする")
		fmt.Println()
		return nil
	},
}

var statusCmd = &cobra.Command{
	Use:   "status",
	Short: "ペットの様子を見る",
	RunE: func(cmd *cobra.Command, args []string) error {
		p, err := getPet()
		if err != nil {
			return err
		}
		msg := applyTimeDecay(p)
		if msg != "" {
			fmt.Println("\n  " + msg)
		}
		p.LastSeen = time.Now()
		printStatus(p)
		return savePet(p)
	},
}

var feedCmd = &cobra.Command{
	Use:   "feed",
	Short: "ごはんをあげる",
	RunE: func(cmd *cobra.Command, args []string) error {
		p, err := getPet()
		if err != nil {
			return err
		}
		applyTimeDecay(p)

		before := p.Hunger
		p.Hunger = clamp(p.Hunger+feedAmount, 0, maxStat)
		gained := p.Hunger - before
		p.LastSeen = time.Now()

		fmt.Println()
		if gained == 0 {
			fmt.Printf("  %s 「もうおなかいっぱいだよ〜！」\n", p.Name)
		} else {
			fmt.Printf("  %s 「もぐもぐ…おいしい！（+%d）」\n", p.Name, gained)
			p.Happiness = clamp(p.Happiness+5, 0, maxStat)
		}
		fmt.Println()
		printStatus(p)
		return savePet(p)
	},
}

var playCmd = &cobra.Command{
	Use:   "play",
	Short: "一緒に遊ぶ",
	RunE: func(cmd *cobra.Command, args []string) error {
		p, err := getPet()
		if err != nil {
			return err
		}
		applyTimeDecay(p)

		if p.Energy < 20 {
			fmt.Printf("\n  %s 「つかれた…あそべないよ…」\n\n", p.Name)
			printStatus(p)
			return savePet(p)
		}

		before := p.Happiness
		p.Happiness = clamp(p.Happiness+playAmount, 0, maxStat)
		gained := p.Happiness - before
		p.Energy = clamp(p.Energy-15, 0, maxStat)
		p.Hunger = clamp(p.Hunger-10, 0, maxStat)
		p.LastSeen = time.Now()

		games := []string{"かくれんぼ", "ボール遊び", "追いかけっこ", "なぞなぞ"}
		game := games[p.Age%len(games)]

		fmt.Println()
		fmt.Printf("  %s と%sをして遊んだ！（happiness +%d）\n", p.Name, game, gained)
		fmt.Printf("  %s 「たのしかった〜！またやろうね！」\n", p.Name)
		fmt.Println()
		printStatus(p)
		return savePet(p)
	},
}

var restCmd = &cobra.Command{
	Use:   "rest",
	Short: "休ませる",
	RunE: func(cmd *cobra.Command, args []string) error {
		p, err := getPet()
		if err != nil {
			return err
		}
		applyTimeDecay(p)

		before := p.Energy
		p.Energy = clamp(p.Energy+restAmount, 0, maxStat)
		gained := p.Energy - before
		p.LastSeen = time.Now()

		fmt.Println()
		if gained == 0 {
			fmt.Printf("  %s 「もう元気いっぱいだよ！」\n", p.Name)
		} else {
			fmt.Printf("  %s 「すやすや… zzz（energy +%d）」\n", p.Name, gained)
		}
		fmt.Println()
		printStatus(p)
		return savePet(p)
	},
}

var goodbyeCmd = &cobra.Command{
	Use:   "goodbye",
	Short: "ペットとお別れする（データ削除）",
	RunE: func(cmd *cobra.Command, args []string) error {
		p, err := getPet()
		if err != nil {
			return err
		}
		fmt.Printf("\n  %s 「いままでありがとう…またね…」\n\n", p.Name)
		fmt.Printf("  %s との %d 日間の思い出を胸に…\n\n", p.Name, p.Age)
		return os.Remove(statePath())
	},
}

func getPet() (*Pet, error) {
	p, err := loadPet()
	if err != nil {
		return nil, err
	}
	if p == nil {
		return nil, fmt.Errorf("ペットがいません。`pet new <name>` で迎えてあげてね")
	}
	return p, nil
}

func Execute() error {
	return rootCmd.Execute()
}

func init() {
	rootCmd.AddCommand(newCmd, statusCmd, feedCmd, playCmd, restCmd, goodbyeCmd)
}
