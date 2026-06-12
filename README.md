# 資科系活動相簿

這是一個 Django 活動管理與相簿系統。一般訪客可以瀏覽活動列表與活動照片，系學會會員登入後可以查看活動附件，老師帳號可以新增、編輯、刪除活動，並替活動上傳照片與附件。

## 功能

- 公開瀏覽活動列表
- 公開瀏覽活動詳情與照片
- 系學會成員可申請帳號
- 老師可在 Django Admin 將帳號加入「系學會會員」群組
- 系學會會員限定查看與下載活動附件
- 老師限定新增、編輯、刪除活動
- 老師限定上傳活動照片與附件
- 使用 Django 內建帳號系統管理老師權限
- 使用 SQLite 儲存資料，使用 `MEDIA_ROOT` 儲存照片與附件檔案

## 權限

| 身分 | 看活動 + 照片 | 看附件 | 上傳/刪除附件 |
| --- | --- | --- | --- |
| 一般訪客 | 可以 | 不可以 | 不可以 |
| 已註冊但未審核帳號 | 可以 | 不可以 | 不可以 |
| 系學會會員 | 可以 | 可以 | 不可以 |
| 老師 `staff` | 可以 | 可以 | 可以 |

老師帳號使用 Django Admin 的 `Staff status` 判斷，也就是 `is_staff=True`。

系學會會員使用 Django 內建 Group 管理，群組名稱為「系學會會員」。學生可自行申請帳號，但帳號建立後預設尚未加入群組；老師需到 `/admin/` 的使用者管理頁，把該帳號加入「系學會會員」群組後，該帳號才可以查看與下載附件。

## 建議開發環境

依照本機規範，建議使用 `uv` 建立 Python 虛擬環境。此工作區目前未附 `pyproject.toml`，若要補齊可建立專案設定並加入 Django 與 Pillow。

```powershell
uv venv
uv add django pillow
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

若目前系統已安裝 Django，也可以直接執行：

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## 主要路由

- `/`：活動列表
- `/<活動 ID>/`：活動詳情
- `/accounts/signup/`：申請系學會會員帳號
- `/accounts/login/`：會員登入
- `/accounts/logout/`：會員登出
- `/documents/<附件 ID>/download/`：下載附件，限系學會會員與老師
- `/manage/`：老師管理首頁
- `/manage/members/`：人員管理，限老師核准或移除系學會會員資格
- `/manage/create/`：新增活動，限老師
- `/manage/<活動 ID>/edit/`：編輯活動，限老師
- `/manage/<活動 ID>/delete/`：刪除活動，限老師
- `/manage/<活動 ID>/photos/`：管理照片，限老師
- `/manage/<活動 ID>/documents/`：管理附件，限老師
- `/admin/`：Django 後台

## 測試

```powershell
python manage.py test
```
