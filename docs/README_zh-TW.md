# Project Standards

[English](../README.md) · **繁體中文**

`project-standards` 是一個 [Agent Skill](https://agentskills.io/)，用於建立並維護 repository 的開發標準，以及引導 coding agent 讀取這些標準的 `AGENTS.md`。

它會先讀取 repository，只詢問無法自行推斷的決策，並依各個 application 的範圍撰寫標準，讓 monorepo 中的 application 不會繼承彼此的規則。對於內建 toolchain profile 的語言，它還能設定 formatter、linter、type checker 與測試框架，讓規則由工具而不是文字說明來強制執行。

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

## 文件

- [Usage](usage.md)：建立、更新與編輯標準、Skill 會詢問的設定，以及 Skill 如何保持最新。
- [Generated files](generated-files.md)：Skill 產生的檔案與各檔案的內容。
- [Toolchain profiles](toolchain-profiles.md)：內建的 formatter、linter、type checker 與測試框架設定。
- [Design principles](design-principles.md)：標準為何以這種方式組織。

## License

[MIT](../LICENSE) License.
