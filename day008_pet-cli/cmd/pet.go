package cmd

import (
	"encoding/json"
	"fmt"
	"math/rand"
	"os"
	"path/filepath"
	"time"
)

const (
	maxStat      = 100
	hungerDecay  = 10 // per hour
	happyDecay   = 8  // per hour
	energyDecay  = 6  // per hour
	feedAmount   = 30
	playAmount   = 25
	restAmount   = 35
)

type Pet struct {
	Name      string    `json:"name"`
	Hunger    int       `json:"hunger"`    // 0=starving, 100=full
	Happiness int       `json:"happiness"` // 0=sad, 100=ecstatic
	Energy    int       `json:"energy"`    // 0=exhausted, 100=energized
	Age       int       `json:"age"`       // days
	LastSeen  time.Time `json:"last_seen"`
	BornAt    time.Time `json:"born_at"`
}

func statePath() string {
	home, _ := os.UserHomeDir()
	return filepath.Join(home, ".pet-cli", "pet.json")
}

func loadPet() (*Pet, error) {
	path := statePath()
	data, err := os.ReadFile(path)
	if os.IsNotExist(err) {
		return nil, nil
	}
	if err != nil {
		return nil, err
	}
	var p Pet
	if err := json.Unmarshal(data, &p); err != nil {
		return nil, err
	}
	return &p, nil
}

func savePet(p *Pet) error {
	path := statePath()
	if err := os.MkdirAll(filepath.Dir(path), 0755); err != nil {
		return err
	}
	data, err := json.MarshalIndent(p, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, data, 0644)
}

func clamp(v, min, max int) int {
	if v < min {
		return min
	}
	if v > max {
		return max
	}
	return v
}

// applyTimeDecay reduces stats based on elapsed time since last interaction.
func applyTimeDecay(p *Pet) string {
	elapsed := time.Since(p.LastSeen)
	hours := elapsed.Hours()
	if hours < 0.016 { // less than ~1 minute, skip
		return ""
	}

	hungerLost := int(hours * hungerDecay)
	happyLost := int(hours * happyDecay)
	energyLost := int(hours * energyDecay)

	p.Hunger = clamp(p.Hunger-hungerLost, 0, maxStat)
	p.Happiness = clamp(p.Happiness-happyLost, 0, maxStat)
	p.Energy = clamp(p.Energy-energyLost, 0, maxStat)

	// Age in days
	p.Age = int(time.Since(p.BornAt).Hours() / 24)

	var msg string
	if hours >= 4 {
		msg = fmt.Sprintf("⏰ %s missed you for %.1f hours...", p.Name, hours)
	}
	return msg
}

func moodEmoji(p *Pet) string {
	avg := (p.Hunger + p.Happiness + p.Energy) / 3
	switch {
	case avg >= 80:
		return "（＾▽＾）"
	case avg >= 60:
		return "（・ω・）"
	case avg >= 40:
		return "（－_－）"
	case avg >= 20:
		return "（；ω；）"
	default:
		return "（x_x）"
	}
}

func statBar(label string, val int) string {
	filled := val / 5
	bar := ""
	for i := 0; i < 20; i++ {
		if i < filled {
			bar += "█"
		} else {
			bar += "░"
		}
	}
	return fmt.Sprintf("%-10s [%s] %3d", label, bar, val)
}

func randomSay(lines []string) string {
	return lines[rand.Intn(len(lines))]
}

func printStatus(p *Pet) {
	fmt.Println()
	fmt.Printf("  %s  %s  (Day %d)\n", moodEmoji(p), p.Name, p.Age)
	fmt.Println()
	fmt.Println("  " + statBar("🍖 Hunger", p.Hunger))
	fmt.Println("  " + statBar("💛 Happy ", p.Happiness))
	fmt.Println("  " + statBar("⚡ Energy", p.Energy))
	fmt.Println()

	avg := (p.Hunger + p.Happiness + p.Energy) / 3
	var mood string
	switch {
	case avg >= 80:
		mood = randomSay([]string{
			"「すごく元気だよ！遊ぼう！」",
			"「今日も最高だ〜！」",
			"「ごはんおいしかった！」",
		})
	case avg >= 60:
		mood = randomSay([]string{
			"「まあまあかな…」",
			"「ちょっと眠いかも」",
		})
	case avg >= 40:
		mood = randomSay([]string{
			"「おなかすいたなぁ…」",
			"「かまってほしいな…」",
		})
	case avg >= 20:
		mood = randomSay([]string{
			"「つらいよ…たすけて…」",
			"「ごはん…まだ？」",
		})
	default:
		mood = "「…もう動けない…」"
	}
	fmt.Printf("  %s %s\n\n", p.Name, mood)
}
