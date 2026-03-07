@echo off
setlocal

set REGION=%~1
if "%REGION%"=="" set REGION=ap-south-1

set DEEPAR_ENDPOINT=%~2
if "%DEEPAR_ENDPOINT%"=="" set DEEPAR_ENDPOINT=%AI_SAHAYAK_DEEPAR_ENDPOINT%

set LAMBDA_FN=%~3
if "%LAMBDA_FN%"=="" set LAMBDA_FN=ai-sahayak-festival-orchestrator

set RULE_DAILY=%~4
if "%RULE_DAILY%"=="" set RULE_DAILY=ai-sahayak-daily-forecast

set RULE_FESTIVAL=%~5
if "%RULE_FESTIVAL%"=="" set RULE_FESTIVAL=-

set AWSCLI_EXE=C:\Program Files\Amazon\AWSCLIV2\aws.exe
if not exist "%AWSCLI_EXE%" set AWSCLI_EXE=aws

set FAIL=0

echo ==============================================
echo AI Sahayak AWS Setup Validation
echo Region            : %REGION%
echo DeepAR Endpoint   : %DEEPAR_ENDPOINT%
echo Lambda Function   : %LAMBDA_FN%
echo Rule (Daily)      : %RULE_DAILY%
echo Rule (Festival)   : %RULE_FESTIVAL%
echo CLI               : %AWSCLI_EXE%
echo ==============================================

echo.
echo --- STS identity ---
"%AWSCLI_EXE%" sts get-caller-identity --output json
if errorlevel 1 (
  echo [FAIL] STS identity
  set FAIL=1
) else (
  echo [PASS] STS identity
)

echo.
echo --- Bedrock model access ---
"%AWSCLI_EXE%" bedrock list-foundation-models --region %REGION% --output json
if errorlevel 1 (
  echo [FAIL] Bedrock model access
  set FAIL=1
) else (
  echo [PASS] Bedrock model access
)

if not "%DEEPAR_ENDPOINT%"=="" (
  echo.
  echo --- SageMaker endpoint exists ---
  "%AWSCLI_EXE%" sagemaker describe-endpoint --endpoint-name %DEEPAR_ENDPOINT% --region %REGION% --output json
  if errorlevel 1 (
    echo [FAIL] SageMaker endpoint exists
    set FAIL=1
  ) else (
    echo [PASS] SageMaker endpoint exists
  )
) else (
  echo.
  echo [WARN] AI_SAHAYAK_DEEPAR_ENDPOINT not set. Skipping SageMaker endpoint check.
)

echo.
echo --- Lambda function exists ---
"%AWSCLI_EXE%" lambda get-function --function-name %LAMBDA_FN% --region %REGION% --output json
if errorlevel 1 (
  echo [FAIL] Lambda function exists
  set FAIL=1
) else (
  echo [PASS] Lambda function exists
)

echo.
echo --- EventBridge daily rule exists ---
"%AWSCLI_EXE%" events describe-rule --name %RULE_DAILY% --region %REGION% --output json
if errorlevel 1 (
  echo [FAIL] EventBridge daily rule exists
  set FAIL=1
) else (
  echo [PASS] EventBridge daily rule exists
)

echo.
echo --- EventBridge holi rule exists ---
if "%RULE_FESTIVAL%"=="-" (
  echo [INFO] Festival rule not requested. Skipping optional check.
) else (
  echo --- EventBridge festival rule exists ---
  "%AWSCLI_EXE%" events describe-rule --name %RULE_FESTIVAL% --region %REGION% --output json
  if errorlevel 1 (
    echo [FAIL] EventBridge festival rule exists
    set FAIL=1
  ) else (
    echo [PASS] EventBridge festival rule exists
  )
)

echo.
if "%FAIL%"=="0" (
  echo [PASS] All requested checks passed.
  exit /b 0
) else (
  echo [FAIL] One or more checks failed. Review output above.
  exit /b 1
)
