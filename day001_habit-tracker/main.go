package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"
)

const (
	dataFileName = ".habit-tracker.json"
	dateFormat   = "2006-01-02"
)

const (
	colorReset  = "\033[0m"
	colorGreen  = "\033[32m"
	colorRed    = "\033[31m"
	colorYellow = "\033[33m"
	colorCyan   = "\033[36m"
	colorBold   = "\033[1m"
	colorGray   = "\033[90m"
)

type Habit struct {
	Name      string   `json:"name"`
	CreatedAt string   `json:"created_at"`
	DoneDates []string `json:"done_dates"`
}

type Store struct {
	Habits []Habit `json:"habits"`
}

func dataFilePath() (string, error) {
	home, err := os.UserHomeDir()
	if err != nil {
		return "", fmt.Errorf("ホームディレクトリを取得できません: %w", err)
	}
	return filepath.Join(home, dataFileName), nil
}

func loadStore() (Store, error) {
	path, err := dataFilePath()
	if err != nil {
		return Store{}, err
	}

	data, err := os.ReadFile(path)
	if os.IsNotExist(err) {
		return Store{Habits: []Habit{}}, nil
	}
	if err != nil {
		return Store{}, fmt.Errorf("データファイルを読み込めません: %w", err)
	}

	var store Store
	if err := json.Unmarshal(data, &store); err != nil {
		return Store{}, fmt.Errorf("データのパースに失敗しました: %w", err)
	}
	if store.Habits == nil {
		store.Habits = []Habit{}
	}
	return store, nil
}

func saveStore(store Store) error {
	path, err := dataFilePath()
	if err != nil {
		return err
	}

	data, err := json.MarshalIndent(store, "", "  ")
	if err != nil {
		return fmt.Errorf("データのシリアライズに失敗しました: %w", err)
	}

	if err := os.WriteFile(path, data, 0600); err != nil {
		return fmt.Errorf("データファイルを書き込めません: %w", err)
	}
	return nil
}

func today() string {
	return time.Now().Format(dateFormat)
}

func findHabit(habits []Habit, name string) (int, bool) {
	for i, h := range habits {
		if strings.EqualFold(h.Name, name) {
			return i, true
		}
	}
	return -1, false
}

func isDoneToday(habit Habit) bool {
	t := today()
	for _, d := range habit.DoneDates {
		if d == t {
			return true
		}
	}
	return false
}

func calcStreak(habit Habit) int {
	if len(habit.DoneDates) == 0 {
		return 0
	}

	sorted := make([]string, len(habit.DoneDates))
	copy(sorted, habit.DoneDates)
	sort.Strings(sorted)

	doneSet := map[string]bool{}
	for _, d := range sorted {
		doneSet[d] = true
	}

	streak := 0
	check := today()
	for {
		if !doneSet[check] {
			break
		}
		streak++
		t, _ := time.Parse(dateFormat, check)
		check = t.AddDate(0, 0, -1).Format(dateFormat)
	}
	return streak
}

func cmdAdd(name string) error {
	store, err := loadStore()
	if err != nil {
		return err
	}

	if _, exists := findHabit(store.Habits, name); exists {
		return fmt.Errorf("習慣 %q はすでに存在します", name)
	}

	newHabit := Habit{
		Name:      name,
		CreatedAt: today(),
		DoneDates: []string{},
	}
	newHabits := append(store.Habits, newHabit)
	newStore := Store{Habits: newHabits}

	if err := saveStore(newStore); err != nil {
		return err
	}

	fmt.Printf("%s✓%s 習慣 %q を追加しました\n", colorGreen, colorReset, name)
	return nil
}

func cmdDone(name string) error {
	store, err := loadStore()
	if err != nil {
		return err
	}

	idx, exists := findHabit(store.Habits, name)
	if !exists {
		return fmt.Errorf("習慣 %q が見つかりません", name)
	}

	habit := store.Habits[idx]

	if isDoneToday(habit) {
		fmt.Printf("%s既に今日は完了しています%s: %s\n", colorYellow, colorReset, habit.Name)
		return nil
	}

	newDates := append(habit.DoneDates, today())
	updatedHabit := Habit{
		Name:      habit.Name,
		CreatedAt: habit.CreatedAt,
		DoneDates: newDates,
	}

	newHabits := make([]Habit, len(store.Habits))
	copy(newHabits, store.Habits)
	newHabits[idx] = updatedHabit
	newStore := Store{Habits: newHabits}

	if err := saveStore(newStore); err != nil {
		return err
	}

	streak := calcStreak(updatedHabit)
	fmt.Printf("%s✓%s %s — 完了！ ストリーク: %s%d 日%s\n",
		colorGreen, colorReset, updatedHabit.Name, colorYellow, streak, colorReset)
	return nil
}

func cmdList() error {
	store, err := loadStore()
	if err != nil {
		return err
	}

	if len(store.Habits) == 0 {
		fmt.Printf("%s習慣が登録されていません。`habit add <名前>` で追加してください。%s\n",
			colorGray, colorReset)
		return nil
	}

	fmt.Printf("%s%s今日の習慣 (%s)%s\n\n", colorBold, colorCyan, today(), colorReset)

	doneCount := 0
	for _, h := range store.Habits {
		streak := calcStreak(h)
		if isDoneToday(h) {
			doneCount++
			fmt.Printf("  %s[✓]%s %-24s ストリーク: %s%d 日%s\n",
				colorGreen, colorReset, h.Name, colorYellow, streak, colorReset)
		} else {
			fmt.Printf("  %s[ ]%s %-24s ストリーク: %s%d 日%s\n",
				colorGray, colorReset, h.Name, colorGray, streak, colorReset)
		}
	}

	fmt.Printf("\n  %s%d / %d 完了%s\n", colorBold, doneCount, len(store.Habits), colorReset)
	return nil
}

func cmdStreak(name string) error {
	store, err := loadStore()
	if err != nil {
		return err
	}

	idx, exists := findHabit(store.Habits, name)
	if !exists {
		return fmt.Errorf("習慣 %q が見つかりません", name)
	}

	habit := store.Habits[idx]
	streak := calcStreak(habit)
	total := len(habit.DoneDates)

	fmt.Printf("%s%s%s\n", colorBold, habit.Name, colorReset)
	fmt.Printf("  現在のストリーク: %s%d 日%s\n", colorYellow, streak, colorReset)
	fmt.Printf("  総完了回数      : %d 回\n", total)
	fmt.Printf("  開始日          : %s\n", habit.CreatedAt)
	return nil
}

func cmdHistory(name string) error {
	store, err := loadStore()
	if err != nil {
		return err
	}

	idx, exists := findHabit(store.Habits, name)
	if !exists {
		return fmt.Errorf("習慣 %q が見つかりません", name)
	}

	habit := store.Habits[idx]
	doneSet := map[string]bool{}
	for _, d := range habit.DoneDates {
		doneSet[d] = true
	}

	now := time.Now()
	start := now.AddDate(0, 0, -29)

	fmt.Printf("%s%s%s — 過去 30 日\n\n", colorBold, habit.Name, colorReset)

	weekLabels := []string{"月", "火", "水", "木", "金", "土", "日"}
	fmt.Print("  ")
	for _, w := range weekLabels {
		fmt.Printf("%s ", w)
	}
	fmt.Println()

	// 月曜始まりで週頭に空白を埋める（0=月, 6=日）
	startWd := int(start.Weekday())
	if startWd == 0 {
		startWd = 6
	} else {
		startWd--
	}

	fmt.Print("  ")
	for i := 0; i < startWd; i++ {
		fmt.Print("  ")
	}

	for i := 0; i < 30; i++ {
		d := start.AddDate(0, 0, i)
		ds := d.Format(dateFormat)

		wd := int(d.Weekday())
		if wd == 0 {
			wd = 6
		} else {
			wd--
		}

		if wd == 0 && i > 0 {
			fmt.Println()
			fmt.Print("  ")
		}

		if doneSet[ds] {
			fmt.Printf("%s●%s ", colorGreen, colorReset)
		} else if d.After(now) {
			fmt.Printf("%s·%s ", colorGray, colorReset)
		} else {
			fmt.Printf("%s○%s ", colorGray, colorReset)
		}
	}
	fmt.Println()
	return nil
}

func cmdDelete(name string) error {
	store, err := loadStore()
	if err != nil {
		return err
	}

	idx, exists := findHabit(store.Habits, name)
	if !exists {
		return fmt.Errorf("習慣 %q が見つかりません", name)
	}

	deletedName := store.Habits[idx].Name
	newHabits := make([]Habit, 0, len(store.Habits)-1)
	for i, h := range store.Habits {
		if i != idx {
			newHabits = append(newHabits, h)
		}
	}

	if err := saveStore(Store{Habits: newHabits}); err != nil {
		return err
	}

	fmt.Printf("%s✓%s 習慣 %q を削除しました\n", colorYellow, colorReset, deletedName)
	return nil
}

func printUsage() {
	fmt.Printf(`%s%shabit%s — 習慣トラッカー CLI%s

%sUsage:%s
  habit <command> [args]

%sCommands:%s
  add <name>       習慣を追加
  done <name>      今日の習慣を完了としてマーク
  list             今日の習慣一覧を表示
  streak <name>    ストリーク情報を表示
  history <name>   過去 30 日のカレンダーを表示
  delete <name>    習慣を削除
  help             このヘルプを表示

%sExamples:%s
  habit add "毎日読書"
  habit done "毎日読書"
  habit list
  habit streak "毎日読書"
  habit history "毎日読書"

%sStorage:%s
  ~/.habit-tracker.json
`,
		colorBold, colorCyan, colorReset, colorReset,
		colorBold, colorReset,
		colorBold, colorReset,
		colorBold, colorReset,
		colorBold, colorReset,
	)
}

func main() {
	args := os.Args[1:]
	if len(args) == 0 {
		printUsage()
		return
	}

	cmd := args[0]
	rest := strings.Join(args[1:], " ")

	var err error
	switch cmd {
	case "add":
		if rest == "" {
			fmt.Fprintln(os.Stderr, "使い方: habit add <name>")
			os.Exit(1)
		}
		err = cmdAdd(rest)
	case "done":
		if rest == "" {
			fmt.Fprintln(os.Stderr, "使い方: habit done <name>")
			os.Exit(1)
		}
		err = cmdDone(rest)
	case "list":
		err = cmdList()
	case "streak":
		if rest == "" {
			fmt.Fprintln(os.Stderr, "使い方: habit streak <name>")
			os.Exit(1)
		}
		err = cmdStreak(rest)
	case "history":
		if rest == "" {
			fmt.Fprintln(os.Stderr, "使い方: habit history <name>")
			os.Exit(1)
		}
		err = cmdHistory(rest)
	case "delete":
		if rest == "" {
			fmt.Fprintln(os.Stderr, "使い方: habit delete <name>")
			os.Exit(1)
		}
		err = cmdDelete(rest)
	case "help", "--help", "-h":
		printUsage()
	default:
		fmt.Fprintf(os.Stderr, "%sエラー:%s 不明なコマンド %q\n", colorRed, colorReset, cmd)
		fmt.Fprintln(os.Stderr, "`habit help` でコマンド一覧を確認してください。")
		os.Exit(1)
	}

	if err != nil {
		fmt.Fprintf(os.Stderr, "%sエラー:%s %v\n", colorRed, colorReset, err)
		os.Exit(1)
	}
}
