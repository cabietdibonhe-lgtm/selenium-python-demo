#!/usr/bin/env bash
set -e

echo "=== Install deps (CI) ==="

export CI=true

python3 -m pip install --upgrade pip
pip3 install -r requirements.txt

# chuẩn bị thư mục để publish artifacts (không bị 'not found')
mkdir -p allure-results logs screenshots
