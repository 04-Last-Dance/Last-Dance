---
Date_of_creation: 2025-01-15 수 05:54:07
Last_modified:
  - 2025-05-10 토 21:47:29
  - 2025-05-08 목 20:52:01
  - 2025-05-07 수 01:48:47
  - 2025-04-15 화 19:36:27
  - 2025-04-13 일 15:09:33
  - 2025-04-12 토 21:18:22
  - 2025-01-15 수 05:54:07
aliases:
  - 깃 커밋 메시지 관습
  - 관습(Git)
  - 관례(Git)
tags:
  - "#R"
Reference:
  - https://velog.io/@archivvonjang/Git-Commit-Message-Convention
  - https://gitmoji.dev/
  - https://github.com/gyoogle/tech-interview-for-developer/blob/master/ETC/Git%20Commit%20Message%20Convention.md
  - https://velog.io/@jiheon/Git-Commit-message-%EA%B7%9C%EC%B9%99
  - https://beomseok95.tistory.com/328
  - https://blog.munilive.com/posts/my-git-commit-guide.html
  - https://meetup.nhncloud.com/posts/106
  - https://beandeveloper.tistory.com/12
---
# Git Commit Message Convention
---
## 1. 커밋 메시지 구조
---
```
type(scope): subject

body

footer
```

- 각 파트는 빈 줄로 구분합니다
- scope는 선택사항이며, 사용 시 **항상 소문자**로 작성하는 것을 권장합니다.   ^69eea8
  - 이는 Gitmoji, Conventional Commits 등 주요 스타일 가이드의 관례를 따르기 위함입니다.  
  - ✅ 예시: `feat(api)`, `fix(db)`, `docs(readme)`  
  - ❌ `docs(Readme)`나 `docs(README)`처럼 대문자를 포함한 scope는 사용하지 않습니다.

## 2. 커밋 타입 (Type)
---
`<type>`은 **해당 Commit의 성격**을 나타내며 다음 중 하나여야 한다.

| 타입               | 설명                      |
| ---------------- | ----------------------- |
| feat             | 새로운 기능 추가               |
| fix              | 버그 수정                   |
| build            | 빌드 관련 파일 수정 / 모듈 설치, 삭제 |
| chore            | 자잘한 수정이나 반복 업무 커밋       |
| ci               | CI 설정 파일 관련 커밋          |
| docs             | 문서 수정                   |
| style            | 코드 스타일 혹은 포맷팅 변경        |
| refactor         | 코드 리팩토링                 |
| test             | 테스트 코드, 리팩토링 테스트 코드 추가  |
| release          | 버전 릴리즈                  |
| design           | CSS 등 사용자 UI 디자인 변경     |
| comment          | 필요한 주석 추가 및 변경          |
| rename           | 파일/폴더명 수정 또는 이동         |
| remove           | 파일 삭제                   |
| perf             | 성능 개선                   |
| !BREAKING CHANGE | 커다란 API 변경              |
| !HOTFIX          | 급하게 치명적인 버그를 고치는 경우     |

## 3. 제목 (Subject) 규칙
---
1. 제목과 본문은 **빈 행으로 구분**
2. 제목은 **50자 이내**로 작성
3. 제목의 **첫 글자는 대문자**로 작성
4. 제목 끝에는 **마침표를 넣지 않는다**
5. **명령문**으로 작성(동사 원형 사용) 및 과거형을 사용하지 않음
    - "Fixed" → "Fix"
    - "Added" → "Add"
6. <b>어떻게(How)</b>보다 <b>무엇을, 왜(What, Why)</b>에 맞춰 작성

## 4. 본문 (Body) 규칙
---
- 선택 사항이며 모든 커밋에 작성할 필요 없음
	1. 한 줄당 72자를 넘기지 않음
	2. 여러 줄의 메시지를 작성할 땐 `-`로 구분
	3. <b>어떻게(How)</b>보다 <b>무엇을, 왜(What, Why)</b>에 맞춰 작성

## 5. 꼬리말 (Footer) 규칙
---
이슈 트래커 ID를 명시할 때 사용:

| 유형         | 설명           |
| ---------- | ------------ |
| Fixes      | 이슈 수정중 (미해결) |
| Resolves   | 이슈 해결        |
| Ref        | 참고할 이슈       |
| Related to | 관련된 이슈       |

- `유형: #이슈번호` 형식으로 작성
- 여러 개의 이슈번호는 쉼표(,)로 구분
    - 예: `Resolves: #123, #456`
- close는 이슈를 참조하면서 main브랜치로 푸시될 때 이슈를 닫게 됩니다.

## 6. 커밋 메시지 예시
---
```
feat: 회원 가입 기능 구현

- 이메일 인증 기능 추가
- 비밀번호 암호화 처리
- 중복 아이디 검사 로직 구현

Resolves: #123
Related to: #456, #789
```

## 7. Gitmoji 가이드
---
주요 이모지와 의미:

| 이모지 |            코드            | 의미              |
| :-: | :----------------------: | :-------------- |
| 🎨  |         `:art:`          | 코드의 구조/형태 개선    |
| ⚡️  |         `:zap:`          | 성능 개선           |
| 🐛  |         `:bug:`          | 버그 수정           |
|  ✨  |       `:sparkles:`       | 새 기능            |
| 📝  |         `:memo:`         | 문서 추가/수정        |
| 🔥  |         `:fire:`         | 코드/파일 삭제        |
| 🚑  |      `:ambulance:`       | 긴급 수정           |
| 💄  |       `:lipstick:`       | UI/스타일 파일 추가/수정 |
| ♻️  |       `:recycle:`        | 코드 리팩토링         |
| 🔧  |        `:wrench:`        | 설정 파일 추가/수정     |
| 🌐  | `:globe_with_meridians:` | 국제화/현지화         |
|  ✅  |   `:white_check_mark:`   | 테스트 추가/수정       |
| 🔒  |         `:lock:`         | 보안 이슈 수정        |
| 🚀  |        `:rocket:`        | 배포 관련           |
