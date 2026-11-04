# Project Standards

[English](../README.md) · **繁體中文**

`project-standards` 是一個 [Agent Skill](https://agentskills.io/)，用於建立並管理專案的開發規範與開發標準。

## 安裝

### Skills CLI（`npx skills`）

```bash
npx skills@latest add hmes98318/project-standards
```

### Claude Code

```bash
/plugin marketplace add hmes98318/project-standards
/plugin install project-standards@project-standards
```

### Codex

```bash
codex plugin marketplace add hmes98318/project-standards
codex plugin add project-standards@project-standards
```

## 使用

在要建立或更新開發標準的 repository 中，要求 agent：

```text
Use project-standards SKILL to create or update the development standards for this repository.
```

Skill 會先讀取 repository，再以一個精簡的問題批次確認無法自行推斷的決策。未回答的項目會使用所顯示的預設值。

## 產生的內容

```text
AGENTS.md                            # repository-wide 規則與 routing
CLAUDE.md                            # 選用；匯入 AGENTS.md
<application>/AGENTS.md              # application 不在 repository 根目錄時
docs/standards/
  common/development-guidelines.md   # 固定的 repository-wide 基準
  <application>/                     # 只包含該 application 需要的 standards
```

Application standards 使用固定檔名，且只有在有實質規則時才會建立：

- **軟體 application：** `development.md`、`coding-style.md`、`testing.md`、`security-privacy.md`、`data.md`、`ui.md`、`performance.md`
- **Documentation-only repository：** `development.md`、`writing-style.md`、`testing.md`

## 原則

- **Application scope 是邊界。** Language、framework 與 tooling 相關規則屬於實際擁有它們的 application，monorepo 中的 application 不會互相污染規則。
- **Standards 只保存長期有效的規則，不記錄專案現況。** 目前的 architecture、module layout、deployment state 與 design specification 留在各自的 source-of-truth 文件中，standards 只引用、不複製。
- **開發文檔說明系統的當前狀態。** 產生的 `AGENTS.md` 規則要求 agent 將文檔維護為對現行設計的完整技術說明，就地整合修訂，而不是持續追加修改記錄。
- **`AGENTS.md` 負責 routing，standards 承載細節。** Root 指引不會隨專案成長而變得龐大。
- **既有 tooling 優先。** 先遵循 repository 已強制執行的 formatter、linter 與 compiler 設定；沒有時，依序採用 framework guidance、Google Style Guide、官方 language style guide。
- **Update 優先保留有效決策。** Repository 已有 standards 時，Skill 會重新掃描、保留有效的 user-authored 規則，不假設既有檔案由本 Skill 產生，也不改寫不需要變更的文件。

## 設定

Skill 只會詢問無法從 repository 推斷的設定。

| 設定 | 預設值 |
| --- | --- |
| Documentation root | `docs/` |
| 專案開發文檔語言 | `en-US` |
| Git commit message 語言 | `en-US` |
| Claude Code `CLAUDE.md` adapter | `No`（已在使用時沿用） |
| Coding style | 每個 application 預設 `Automatic`，可覆寫 |
| [程式碼註解策略](../skills/project-standards/SKILL.md#code-comment-policy) | `Full`（或 `Concise`、`None`、`Custom`） |
| 測試策略 | 無預設；每個軟體 application 都會詢問，除非已有明確策略 |

`AGENTS.md` 與 standards 檔案固定使用 `en-US`。預設可建立新的專案開發文檔；若不想建立，請明確告知。這個選擇不會停用 standards 本身，也不會停用既有文件適用的規則。

## 保持最新

產生的 `AGENTS.md` 會要求 agent 在修改文件前先載入 Skill。每個 task 中，Skill 會檢查是否有較新的穩定版（最多每 24 小時查詢一次），不經詢問自動更新，並告知目前使用的版本。若尚未安裝 Skill，agent 會先詢問，才安裝。

檢查由只使用標準函式庫的 Python 3 script 執行，檢查失敗不會阻擋工作。透過 plugin 或 git checkout 安裝的 Skill 不會被原地取代，請用 plugin manager 或 `git` 更新。將 `PROJECT_STANDARDS_NO_UPDATE` 設為任何非空值即可停用檢查。

## License

[MIT](../LICENSE) License。
