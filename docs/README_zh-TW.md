# Project Standards

[English](../README.md) · **繁體中文**

讓 coding agent 依照 repository 的實際結構、tech stack 與既有規範，建立並持續維護可長期使用的開發標準。

`project-standards` 是一個 Agent Skill。它會先檢查專案，再決定哪些規則應該是 repository-wide、哪些應該屬於特定 application，並以 `AGENTS.md` 作為 agent instruction 和 routing layer，將詳細且長期有效的規則維護在 development standards 中。

它不是一組固定模板，也不會把目前的專案狀態直接複製成規範。產生的內容會根據實際 tooling、專案文件、coding-style authority 與使用者決策建立。

## 安裝

### Codex

推薦使用 Codex 原生 Plugin 安裝：

```bash
codex plugin marketplace add hmes98318/project-standards
codex plugin add project-standards@project-standards
```

之後即可在 Codex 中使用 `project-standards` Skill。

### Claude Code

```bash
/plugin marketplace add hmes98318/project-standards
/plugin install project-standards@project-standards
```

### 其他支援 Agent Skills 的工具

若使用支援 Agent Skills 的其他 coding agent，可透過 Skills installer 安裝：

```bash
npx skills@latest add hmes98318/project-standards
```

## 使用

在要建立或更新開發規範的 repository 中要求 agent 使用 `project-standards`：

```text
Use project-standards SKILL to create or update the development standards for this repository.
```

也可以直接描述目的，例如：

```text
Use project-standards SKILL to inspect this repository and update its development standards.
```

Skill 會先讀取 repository，而不是立刻套用通用模板，再以一個精簡的問題批次確認需要使用者決策的設定。

## 它會做什麼

- 掃描 repository layout、application boundaries、languages、frameworks、manifests、build systems、formatters、linters、tests、CI 與既有 development documentation。
- 支援單一 application、monorepo 與 documentation-only repository。
- 建立或更新 repository-wide 與 application-scoped `AGENTS.md` routing。
- 只為實際需要的 application 建立 development standards，不預先產生空白或無關規範。
- 優先遵循 repository 已強制執行的 formatter、linter、compiler 與 code-generation configuration。
- 在沒有專案指定 coding-style authority 時，依序選擇適用的 framework guidance、Google Style Guide 與官方 language style guide。
- 在 update mode 中保留有效的 user-authored rules，而不是整批覆寫既有規範。
- 可選擇建立 thin `CLAUDE.md` adapter，讓 Claude Code 直接沿用相同的 `AGENTS.md` instructions。

## 核心原則

### Application scope 是主要邊界

Language、framework、platform 與 tooling-specific rules 應該屬於實際擁有它們的 application，而不是因為 repository 中出現同一種技術就自動提升成共用規則。

這讓 monorepo 中不同 application 可以維持自己的標準，同時避免規則互相污染。

### Standards 只保存長期有效的規則

Development standards 用來描述「未來應該怎麼開發」，而不是記錄「專案現在長什麼樣子」。

目前的 architecture、module layout、route inventory、deployment state、design specification、feature inventory 或其他 source-of-truth project documentation 不會因為被掃描到，就自動複製進 standards。

Standards 可以引用 authoritative source，但不應該複製會隨實作變動而快速過期的內容。

### `AGENTS.md` 負責 routing，不負責承載所有細節

Root `AGENTS.md` 保存 repository-wide instructions、hard constraints、precedence 與 standards routing。Application-specific `AGENTS.md` 只路由該 application 真正需要的規則。

這讓 agent 可以取得正確的規範，同時避免 root instructions 隨著專案成長變成龐大的單一文件。

### Update 優先保留有效決策

如果 repository 已經有 standards 或 agent instructions，`project-standards` 會先理解現有內容，再進行更新。

它不假設既有文件是由本 Skill 產生，也不會只為了符合模板而改寫沒有實質變更的文件。

## 適合用在

- 新 repository 需要建立一致的 agent-facing development standards。
- 已有 `AGENTS.md` 或 standards，但結構與實際 application boundaries 不一致。
- Monorepo 中不同 application 使用不同語言、framework 或 tooling。
- 專案演進後，既有規範包含過時、重複或已經不適用的內容。
- Standards 混入大量 architecture、design、deployment 或其他描述性 project state，需要重新劃分邊界。
- Documentation-only repository 也需要可執行、可驗證的 development rules。

## 預設行為

`AGENTS.md` 與 development standards 固定使用 `en-US`，確保 agent-facing instructions 一致。

Project development documentation 與 Git commit message 的語言則由使用者選擇，預設為 `en-US`。

Coding style 預設自動依 repository evidence 與 primary documentation 選擇，也可以針對特定 application 覆寫。

## Agent Skills

`project-standards` 採用 [Agent Skills](https://agentskills.io/) 格式，可由支援 `SKILL.md` 的 coding agents 載入與使用。

## License

[MIT](./LICENSE) License。
