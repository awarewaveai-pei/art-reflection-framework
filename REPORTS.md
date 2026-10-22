# SABRDF 報告網站資料串接

網站首頁會讀取 `data/reports.json` 並顯示最近 12 筆報告，支援 `daily`、`weekly`、`monthly`。

## 資料規格

```json
{
  "schema_version": 1,
  "updated_at": null,
  "items": [
    {
      "id": "daily-2026-10-23",
      "type": "daily",
      "date": "2026-10-23",
      "title": "研究情報標題",
      "summary": "已核實的研究摘要",
      "source_url": "https://example.org/source"
    }
  ]
}
```

請勿提交敏感個資、未授權材料、未驗證研究結論或憑空編造的研究新聞。

## 新增報告

進入 GitHub → Actions → **Publish SABRDF report** → Run workflow。輸入報告類別、日期、標題、摘要及可選來源網址。Workflow 將更新 `data/reports.json`；原有 Pages 工作流程會在 main 分支推送後發布網站。

每個 `type + date` 對應一筆報告；再次匯入相同類型同日期將覆蓋舊版本。

**重要限制**：ChatGPT 自動化任務與 GitHub Actions 是兩套獨立系統。建立此資料通道不代表 ChatGPT 排程已自動將報告送進 GitHub；要完全自動化，還需具授權的發布服務或可呼叫 GitHub API 的任務執行環境。請勿把 GitHub Token 放到公開 repo、網站 JavaScript 或 workflow inputs。
