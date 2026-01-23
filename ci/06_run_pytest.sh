#!/usr/bin/env bash
set -e

echo "=== Run pytest (CI) ==="

export CI=true
export PYTHONPATH="$PWD"
export TEST_ENV="ci"

# TeamCity: set parameter (nếu bạn đang dùng parameter này ở step khác)
echo "##teamcity[setParameter name='env.TEST_ENV' value='ci']"

python3 -m pip install --upgrade pip
pip3 install -r requirements.txt

mkdir -p allure-results logs screenshots

# (A) ghi thời gian bắt đầu test
date +%s > logs/start_time.txt

# (B) chạy pytest (có allure + junit)
pytest -m smoke -v \
  --env=ci \
  --project=hello \
  --alluredir=allure-results \
  --junitxml=logs/junit.xml \
  projects/hello/tests

# (C) ghi thời gian kết thúc test
date +%s > logs/end_time.txt

# (D) CHỈ DÙNG ĐỂ TEST SLACK FAIL:
# exit 1
