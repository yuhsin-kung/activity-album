# 資科系活動相簿：ER 圖與系統流程圖

本文件整理專案目前的資料表關聯與主要系統流程，可直接貼到支援 Mermaid 的 Markdown、Mermaid Live Editor，或 draw.io 的 Mermaid 匯入功能使用。

## ER 圖

```mermaid
erDiagram
    AUTH_USER {
        bigint id PK
        string username
        string password
        string first_name
        string email
        boolean is_staff
        boolean is_superuser
        boolean is_active
        datetime date_joined
    }

    AUTH_GROUP {
        integer id PK
        string name
    }

    AUTH_USER_GROUPS {
        integer id PK
        integer user_id FK
        integer group_id FK
    }

    EVENT {
        bigint id PK
        string title
        text description
        date start_date
        date end_date
        string location
        bigint created_by_id FK
        datetime created_at
    }

    EVENT_PHOTO {
        bigint id PK
        bigint event_id FK
        string image
        string caption
        bigint uploaded_by_id FK
        datetime uploaded_at
    }

    EVENT_DOCUMENT {
        bigint id PK
        bigint event_id FK
        string title
        string file
        bigint uploaded_by_id FK
        datetime uploaded_at
    }

    AUTH_USER ||--o{ EVENT : "建立活動 created_by"
    AUTH_USER ||--o{ EVENT_PHOTO : "上傳照片 uploaded_by"
    AUTH_USER ||--o{ EVENT_DOCUMENT : "上傳附件 uploaded_by"
    EVENT ||--o{ EVENT_PHOTO : "包含照片"
    EVENT ||--o{ EVENT_DOCUMENT : "包含附件"
    AUTH_USER ||--o{ AUTH_USER_GROUPS : "擁有群組"
    AUTH_GROUP ||--o{ AUTH_USER_GROUPS : "群組成員"
```

## dbdiagram DBML 版本

可貼到 dbdiagram.io 使用。

```dbml
Table auth_user {
  id bigint [pk]
  username varchar
  password varchar
  first_name varchar
  email varchar
  is_staff boolean
  is_superuser boolean
  is_active boolean
  date_joined datetime
}

Table auth_group {
  id int [pk]
  name varchar
}

Table auth_user_groups {
  id int [pk]
  user_id int [ref: > auth_user.id]
  group_id int [ref: > auth_group.id]
}

Table albums_event {
  id bigint [pk]
  title varchar
  description text
  start_date date
  end_date date
  location varchar
  created_by_id bigint [ref: > auth_user.id]
  created_at datetime
}

Table albums_eventphoto {
  id bigint [pk]
  event_id bigint [ref: > albums_event.id]
  image varchar
  caption varchar
  uploaded_by_id bigint [ref: > auth_user.id]
  uploaded_at datetime
}

Table albums_eventdocument {
  id bigint [pk]
  event_id bigint [ref: > albums_event.id]
  title varchar
  file varchar
  uploaded_by_id bigint [ref: > auth_user.id]
  uploaded_at datetime
}
```

## 系統流程圖

```mermaid
flowchart TD
    START([使用者進入活動相簿系統]) --> LIST[瀏覽活動列表]
    LIST --> DETAIL[查看活動詳情與照片]

    DETAIL --> DOC_CHECK{是否要查看附件?}
    DOC_CHECK -- 否 --> END_PUBLIC([完成瀏覽])
    DOC_CHECK -- 是 --> LOGIN_CHECK{是否已登入?}

    LOGIN_CHECK -- 否 --> LOGIN[登入會員帳號]
    LOGIN --> ROLE_CHECK{身分是否為老師或系學會會員?}
    LOGIN_CHECK -- 是 --> ROLE_CHECK

    ROLE_CHECK -- 否 --> APPLY[申請會員帳號或等待老師審核]
    APPLY --> TEACHER_REVIEW[老師進入會員管理]
    TEACHER_REVIEW --> APPROVE{核准加入系學會會員群組?}
    APPROVE -- 是 --> MEMBER_GROUP[成為系學會會員]
    APPROVE -- 否 --> NO_DOC[無法查看附件]
    MEMBER_GROUP --> DOWNLOAD[查看或下載活動附件]
    ROLE_CHECK -- 是 --> DOWNLOAD
    DOWNLOAD --> END_MEMBER([完成附件瀏覽])

    LIST --> STAFF_LOGIN{是否為老師登入?}
    STAFF_LOGIN -- 否 --> END_PUBLIC
    STAFF_LOGIN -- 是 --> DASHBOARD[進入老師管理首頁]

    DASHBOARD --> EVENT_ACTION{活動管理}
    EVENT_ACTION --> CREATE[新增活動]
    EVENT_ACTION --> UPDATE[編輯活動]
    EVENT_ACTION --> DELETE[刪除活動]

    CREATE --> MEDIA[管理活動媒體]
    UPDATE --> MEDIA
    MEDIA --> PHOTO_ACTION{照片管理}
    PHOTO_ACTION --> UPLOAD_PHOTO[上傳照片]
    PHOTO_ACTION --> DELETE_PHOTO[刪除照片]

    MEDIA --> DOC_ACTION{附件管理}
    DOC_ACTION --> UPLOAD_DOC[上傳附件]
    DOC_ACTION --> DELETE_DOC[刪除附件]

    DASHBOARD --> MEMBER_MANAGE[會員管理]
    MEMBER_MANAGE --> GRANT_MEMBER[核准會員]
    MEMBER_MANAGE --> REVOKE_MEMBER[移除會員資格]

    DASHBOARD --> SUPER_CHECK{是否為超級使用者?}
    SUPER_CHECK -- 是 --> TEACHER_MANAGE[老師權限管理]
    TEACHER_MANAGE --> GRANT_TEACHER[授予老師身分]
    TEACHER_MANAGE --> REVOKE_TEACHER[移除老師身分]
    SUPER_CHECK -- 否 --> END_STAFF([完成管理])

    CREATE --> END_STAFF
    DELETE --> END_STAFF
    UPLOAD_PHOTO --> END_STAFF
    DELETE_PHOTO --> END_STAFF
    UPLOAD_DOC --> END_STAFF
    DELETE_DOC --> END_STAFF
    GRANT_MEMBER --> END_STAFF
    REVOKE_MEMBER --> END_STAFF
    GRANT_TEACHER --> END_STAFF
    REVOKE_TEACHER --> END_STAFF
```

## 主要角色與權限

| 角色 | 可瀏覽活動與照片 | 可查看附件 | 可管理活動 | 可管理照片/附件 | 可管理會員 | 可管理老師 |
| --- | --- | --- | --- | --- | --- | --- |
| 一般訪客 | 是 | 否 | 否 | 否 | 否 | 否 |
| 已註冊但未審核會員 | 是 | 否 | 否 | 否 | 否 | 否 |
| 系學會會員 | 是 | 是 | 否 | 否 | 否 | 否 |
| 老師 staff | 是 | 是 | 是 | 是 | 是 | 否 |
| 超級使用者 superuser | 是 | 是 | 是 | 是 | 是 | 是 |

## 圖表說明

- `Event` 是活動主表，記錄活動名稱、日期區間、地點、說明與建立者。
- `EventPhoto` 是活動照片表，一個活動可以有多張照片。
- `EventDocument` 是活動附件表，一個活動可以有多個附件。
- `auth_user` 是 Django 內建使用者表，用於會員、老師與超級使用者登入。
- `auth_group` 與 `auth_user_groups` 是 Django 內建群組關聯，用來判斷使用者是否屬於「系學會會員」。
- 老師身分使用 `auth_user.is_staff = true` 判斷。
- 超級使用者身分使用 `auth_user.is_superuser = true` 判斷，主要用於授予或移除老師權限。
