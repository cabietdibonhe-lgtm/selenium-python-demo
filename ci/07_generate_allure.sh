#!/usr/bin/env bash
set -e

echo "=== Generate Allure Report ==="

mkdir -p screenshots logs allure-results

if command -v allure >/dev/null 2>&1; then
  allure --version
  allure generate allure-results -o allure-report --clean
  echo "Allure report generated: allure-report/"
else
  echo "WARNING: Allure CLI not found. Skip generating HTML report."
  echo "You can install Allure Commandline on CI agent or generate locally."
fi
