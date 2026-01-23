#!/usr/bin/env bash
set -euo pipefail

echo "=== Notify Slack (FAIL) via BOT TOKEN ==="
pwd
ls -la

# (1) Chuẩn hoá tên biến: ưu tiên SLACK_CHANNEL_ID, vẫn hỗ trợ SLACK_CHANNEL cũ
SLACK_TOKEN="${SLACK_BOT_TOKEN:-}"
CHANNEL="${SLACK_CHANNEL_ID:-${SLACK_CHANNEL:-}}"

echo "DEBUG: SLACK_BOT_TOKEN length = ${#SLACK_TOKEN}"
echo "DEBUG: SLACK_CHANNEL(_ID) = ${CHANNEL}"

if [[ -z "$SLACK_TOKEN" ]]; then
  echo "WARN: SLACK_BOT_TOKEN is empty. Skip Slack notify."
  exit 0
fi
if [[ -z "$CHANNEL" ]]; then
  echo "WARN: SLACK_CHANNEL_ID (or SLACK_CHANNEL) is empty. Skip Slack notify."
  exit 0
fi

export CHANNEL

# ========== ENV ==========
TEST_ENV="${TEST_ENV:-unknown}"
export TEST_ENV

# ========== GIT INFO ==========
GIT_BRANCH="unknown"
GIT_COMMIT="unknown"
GIT_COMMIT_MSG="unknown"

if [ -d ".git" ]; then
  GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
  GIT_COMMIT_MSG=$(git log -1 --pretty=%s 2>/dev/null || echo "unknown")
  GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
else
  echo "== DEBUG: .git not found in this directory =="
fi

export GIT_BRANCH GIT_COMMIT GIT_COMMIT_MSG

BUILD_NAME="UI Automation"
export BUILD_NAME

# ========== TEST SUMMARY ==========
JUNIT_FILE="logs/junit.xml"

TOTAL="unknown"
FAILED="unknown"
SKIPPED="unknown"
PASSED="unknown"
DURATION="unknown"
FAILED_TEST=""
ERROR_MSG=""

if [ -f "$JUNIT_FILE" ]; then
  read -r TOTAL FAILED SKIPPED DURATION <<EOF
$(python3 - <<'PY'
import xml.etree.ElementTree as ET
tree = ET.parse("logs/junit.xml")
root = tree.getroot()

suites = []
if root.tag == "testsuite":
    suites = [root]
elif root.tag == "testsuites":
    suites = root.findall("testsuite")
else:
    suites = [root]

tests = failures = errors = skipped = 0
time = 0.0

for s in suites:
    tests += int(s.attrib.get("tests", 0))
    failures += int(s.attrib.get("failures", 0))
    errors += int(s.attrib.get("errors", 0))
    skipped += int(s.attrib.get("skipped", 0))
    try:
        time += float(s.attrib.get("time", 0.0))
    except:
        pass

failed = failures + errors
print(tests, failed, skipped, f"{time:.2f}s")
PY)
EOF

  if [[ "$TOTAL" =~ ^[0-9]+$ ]] && [[ "$FAILED" =~ ^[0-9]+$ ]] && [[ "$SKIPPED" =~ ^[0-9]+$ ]]; then
    PASSED=$((TOTAL - FAILED - SKIPPED))
  else
    PASSED="unknown"
  fi

  read -r FAILED_TEST ERROR_MSG <<EOF
$(python3 - <<'PY'
import xml.etree.ElementTree as ET
tree = ET.parse("logs/junit.xml")
root = tree.getroot()

for tc in root.iter("testcase"):
    failure = tc.find("failure")
    error = tc.find("error")
    bad = failure if failure is not None else error
    if bad is not None:
        name = tc.attrib.get("name", "")
        cls = tc.attrib.get("classname", "")
        msg = (bad.attrib.get("message", "") or "").replace("\n", " ")[:600]
        print(f"{cls}::{name}", msg)
        break
PY)
EOF
fi

export TOTAL FAILED SKIPPED PASSED DURATION FAILED_TEST ERROR_MSG

# ========== FAIL TYPE ==========
FAIL_TYPE="BUILD FAILED"
if [[ "$FAILED" =~ ^[0-9]+$ ]] && [ "$FAILED" -gt 0 ]; then
  FAIL_TYPE="TEST FAILED"
fi
export FAIL_TYPE

# ========== TIME ==========
START_TIME=$(cat logs/start_time.txt 2>/dev/null || true)
END_TIME=$(cat logs/end_time.txt 2>/dev/null || true)

RUN_TIME="$DURATION"
if [[ "$START_TIME" =~ ^[0-9]+$ ]] && [[ "$END_TIME" =~ ^[0-9]+$ ]] && [ "$END_TIME" -ge "$START_TIME" ]; then
  RUN_TIME="$((END_TIME - START_TIME))s"
fi
export RUN_TIME

# ========== Screenshot: locate robustly ==========
echo "== DEBUG: locate screenshots =="
echo "PWD=$(pwd)"
ls -la screenshots 2>/dev/null || echo "(no screenshots dir)"

LATEST_SHOT=$(
  find screenshots -type f \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" \) \
    -print0 2>/dev/null | xargs -0 ls -1t 2>/dev/null | head -n 1 || true
)
echo "DEBUG: LATEST_SHOT = ${LATEST_SHOT:-<empty>}"

# ========== Build message ==========
MESSAGE_TEXT=$(python3 - <<'PY'
import os
failed = os.environ.get("FAILED","unknown")
lines = [
    f"❌ *{os.environ.get('FAIL_TYPE','BUILD FAILED')}*",
    "",
    f"Environment: {os.environ.get('TEST_ENV','unknown')}",
    f"Branch: {os.environ.get('GIT_BRANCH','unknown')}",
    f"Commit: {os.environ.get('GIT_COMMIT','unknown')} - {os.environ.get('GIT_COMMIT_MSG','unknown')}",
    f"Build: {os.environ.get('BUILD_NAME','UI Automation')}",
    "",
    "Test Summary:",
    f"• Total: {os.environ.get('TOTAL','unknown')}",
    f"• Passed: {os.environ.get('PASSED','unknown')}",
    f"• Failed: {os.environ.get('FAILED','unknown')}",
    f"• Skipped: {os.environ.get('SKIPPED','unknown')}",
    f"• Duration: {os.environ.get('RUN_TIME', os.environ.get('DURATION','unknown'))}",
]
try:
    failed_n = int(failed)
except:
    failed_n = 0
if failed_n > 0:
    ft = os.environ.get("FAILED_TEST","").strip()
    em = os.environ.get("ERROR_MSG","").strip()
    if ft:
        lines += ["", "Failed Test:", ft]
    if em:
        lines += ["", "Error:", em]
lines += ["", "📄 Allure Report:", "(Build → Artifacts → allure-report/index.html)"]
print("\n".join(lines))
PY
)
export MESSAGE_TEXT

# ========== 1) Post message ==========
echo "== DEBUG: postMessage =="
POST_RES=$(curl -sS -X POST "https://slack.com/api/chat.postMessage" \
  -H "Authorization: Bearer $SLACK_TOKEN" \
  -H "Content-type: application/json; charset=utf-8" \
  --data "$(python3 - <<'PY'
import json, os
print(json.dumps({"channel": os.environ["CHANNEL"], "text": os.environ["MESSAGE_TEXT"]}))
PY
)")

echo "DEBUG: postMessage response: $POST_RES"

TS=$(echo "$POST_RES" | python3 -c 'import sys,json; r=json.load(sys.stdin); print(r.get("ts",""))' 2>/dev/null || true)
CHANNEL_ID=$(echo "$POST_RES" | python3 -c 'import sys,json; r=json.load(sys.stdin); print(r.get("channel",""))' 2>/dev/null || true)

echo "DEBUG: thread_ts = $TS"
echo "DEBUG: channel_id = $CHANNEL_ID"

if [[ -z "${TS:-}" || -z "${CHANNEL_ID:-}" ]]; then
  echo "WARN: Cannot get ts/channel from postMessage. Skip screenshot upload."
  exit 0
fi

# ========== 2) Upload screenshot (Slack external upload flow) ==========
if [[ -n "${LATEST_SHOT:-}" && -f "$LATEST_SHOT" ]]; then
  echo "== DEBUG: uploading screenshot via external upload flow =="

  FILE_PATH="$LATEST_SHOT"
  FILE_NAME="$(basename "$FILE_PATH")"
  FILE_SIZE="$(wc -c <"$FILE_PATH" | tr -d ' ')"

  MIME_TYPE="image/png"
  case "$FILE_NAME" in
    *.jpg|*.jpeg) MIME_TYPE="image/jpeg" ;;
    *.png) MIME_TYPE="image/png" ;;
  esac

  echo "DEBUG: filename=$FILE_NAME size=$FILE_SIZE mime=$MIME_TYPE"

  # 2.1) Request upload URL
  UP1_RES=$(curl -sS -X POST "https://slack.com/api/files.getUploadURLExternal" \
    -H "Authorization: Bearer $SLACK_TOKEN" \
    -H "Content-type: application/x-www-form-urlencoded" \
    --data-urlencode "filename=$FILE_NAME" \
    --data-urlencode "length=$FILE_SIZE" \
    --data-urlencode "content_type=$MIME_TYPE")

  echo "DEBUG: getUploadURLExternal response: $UP1_RES"

  UPLOAD_URL=$(echo "$UP1_RES" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("upload_url",""))' 2>/dev/null || echo "")
  FILE_ID=$(echo "$UP1_RES" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("file_id",""))' 2>/dev/null || echo "")

  if [[ -z "$UPLOAD_URL" || -z "$FILE_ID" ]]; then
    ERR=$(echo "$UP1_RES" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("error",""))' 2>/dev/null || echo "unknown")
    echo "WARN: getUploadURLExternal failed. error=$ERR"
    exit 0
  fi

  # 2.2) Upload file
  HTTP_CODE=$(curl -sS -o /dev/null -w "%{http_code}" -X POST "$UPLOAD_URL" \
    -F "filename=@${FILE_PATH};type=${MIME_TYPE}")

  echo "DEBUG: upload_url HTTP status = $HTTP_CODE"
  if [[ "$HTTP_CODE" != "200" ]]; then
    echo "WARN: upload to upload_url failed (HTTP $HTTP_CODE)"
    exit 0
  fi

  # (2) Nếu upload OK thì complete + share vào thread
  COMPLETE_PAYLOAD=$(python3 - <<PY
import json
print(json.dumps({
  "files": [{"id": "$FILE_ID", "title": "Screenshot (latest)"}],
  "channel_id": "$CHANNEL_ID",
  "thread_ts": "$TS",
  "initial_comment": "🖼 Screenshot (latest)"
}))
PY
)

  UP2_RES=$(curl -sS -X POST "https://slack.com/api/files.completeUploadExternal" \
    -H "Authorization: Bearer $SLACK_TOKEN" \
    -H "Content-type: application/json; charset=utf-8" \
    --data "$COMPLETE_PAYLOAD")

  echo "DEBUG: completeUploadExternal response: $UP2_RES"

  OK=$(echo "$UP2_RES" | python3 -c 'import sys,json; r=json.load(sys.stdin); print("true" if r.get("ok") else "false")' 2>/dev/null || echo "false")
  if [[ "$OK" != "true" ]]; then
    ERR=$(echo "$UP2_RES" | python3 -c 'import sys,json; r=json.load(sys.stdin); print(r.get("error",""))' 2>/dev/null || echo "invalid_json_response")
    echo "WARN: completeUploadExternal failed: $ERR"
    echo "HINT: common errors = missing_scope / not_in_channel / channel_not_found / file_uploads_disabled"
  fi
else
  echo "INFO: No screenshot file found to upload."
fi

exit 0
