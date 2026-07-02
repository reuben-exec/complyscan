#Requires -Version 5.1
<#
.SYNOPSIS
    Kimi CLI Auto-Switcher v7 - Uses flat config structure that kimi-cli v1.47.0 expects.
.DESCRIPTION
    1. Reads your Windows env vars
    2. Injects actual API keys into ~/.kimi/config.toml (NO BOM)
    3. Tests API connectivity for all models
    4. Launches kimi with the best working model
.NOTES
    Run with: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    File: start-kimi-auto-v7.ps1
#>

# =============================================================================
# CONFIG PATHS
# =============================================================================

$ConfigPath = Join-Path $env:USERPROFILE ".kimi\config.toml"
$ConfigBackupPath = Join-Path $env:USERPROFILE ".kimi\config.toml.backup"

# =============================================================================
# STEP 1: INJECT API KEYS INTO CONFIG (NO BOM!)
# =============================================================================

Write-Host ""
Write-Host "==============================================================="
Write-Host "  KIMI CLI AUTO-SWITCHER v7"
Write-Host "==============================================================="
Write-Host ""
Write-Host "[STEP 1] Injecting API keys into config.toml (NO BOM)..."

if (-not (Test-Path $ConfigPath)) {
    Write-Host "[ERROR] Config not found at $ConfigPath" -ForegroundColor Red
    Write-Host "  Place kimi_config.toml there first."
    exit 1
}

# Backup existing config
Copy-Item $ConfigPath $ConfigBackupPath -Force -ErrorAction SilentlyContinue

# Read config
$config = Get-Content $ConfigPath -Raw -Encoding UTF8

# Replace placeholders with actual env var values
$replacements = @{
    "{OPENROUTER_API_KEY}"   = $env:OPENROUTER_API_KEY
    "{OPENROUTER_API_KEY2}"  = $env:OPENROUTER_API_KEY2
    "{OPENROUTER_API_KEY3}"  = $env:OPENROUTER_API_KEY3
    "{OPENCODE_ZEN_API_KEY}" = $env:OPENCODE_ZEN_API_KEY
    "{OPENCODE_ZEN_API_KEY2}"= $env:OPENCODE_ZEN_API_KEY2
    "{OPENCODE_ZEN_API_KEY3}"= $env:OPENCODE_ZEN_API_KEY3
    "{GROQ_API_KEY}"         = $env:GROQ_API_KEY
}

$missingKeys = @()
foreach ($placeholder in $replacements.Keys) {
    $value = $replacements[$placeholder]
    if ([string]::IsNullOrEmpty($value)) {
        $missingKeys += $placeholder
        $config = $config -replace [regex]::Escape($placeholder), '""'
    } else {
        $config = $config -replace [regex]::Escape($placeholder), $value
    }
}

# Write WITHOUT BOM using .NET StreamWriter
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($ConfigPath, $config, $utf8NoBom)

Write-Host "  [OK] Config updated with injected keys (no BOM)."

if ($missingKeys.Count -gt 0) {
    Write-Host "  [WARN] Missing keys (set to empty): $($missingKeys -join ', ')" -ForegroundColor Yellow
}

# =============================================================================
# STEP 2: DETECT KIMI BINARY
# =============================================================================

Write-Host ""
Write-Host "[STEP 2] Detecting Kimi installation..."

$kimiCandidates = @(
    ".\ .venv\Scripts\kimi.exe",
    ".venv\Scripts\kimi.exe",
    "kimi"
)
$kimiPath = $null
foreach ($c in $kimiCandidates) {
    if (Test-Path $c -ErrorAction SilentlyContinue) {
        $kimiPath = (Resolve-Path $c).Path
        break
    }
    $cmd = Get-Command $c -ErrorAction SilentlyContinue
    if ($cmd) {
        $kimiPath = $cmd.Source
        break
    }
}

if (-not $kimiPath) {
    Write-Host "[ERROR] kimi CLI not found." -ForegroundColor Red
    exit 1
}

Write-Host "  [OK] Found: $kimiPath"
try {
    $verOutput = & $kimiPath --version 2>&1 | Out-String
    Write-Host "  [OK] Version: $($verOutput.Trim())"
} catch {
    Write-Host "  [WARN] Could not detect version"
}

# =============================================================================
# STEP 3: TEST MODELS
# =============================================================================

Write-Host ""
Write-Host "[STEP 3] Testing models..."
Write-Host ""

$script:WorkingModels = @()
$script:FailedModels = @()

$testModels = @(
    @{ Name="DeepSeek V4 Flash Free (Key)";  Env="OPENCODE_ZEN_API_KEY";  Endpoint="https://opencode.ai/zen/v1/chat/completions"; Model="deepseek-v4-flash-free"; KimiName="DeepSeek V4 Flash Free (Key)"; Provider="OpenCode" },
    @{ Name="DeepSeek V4 Flash Free (Key2)"; Env="OPENCODE_ZEN_API_KEY2"; Endpoint="https://opencode.ai/zen/v1/chat/completions"; Model="deepseek-v4-flash-free"; KimiName="DeepSeek V4 Flash Free (Key2)"; Provider="OpenCode" },
    @{ Name="MiMo V2.5 Free (Key)";         Env="OPENCODE_ZEN_API_KEY";  Endpoint="https://opencode.ai/zen/v1/chat/completions"; Model="mimo-v2.5-free";       KimiName="MiMo V2.5 Free (Key)"; Provider="OpenCode" },
    @{ Name="MiMo V2.5 Free (Key3)";        Env="OPENCODE_ZEN_API_KEY3"; Endpoint="https://opencode.ai/zen/v1/chat/completions"; Model="mimo-v2.5-free";       KimiName="MiMo V2.5 Free (Key3)"; Provider="OpenCode" },
    @{ Name="Big Pickle Free (Key)";        Env="OPENCODE_ZEN_API_KEY";  Endpoint="https://opencode.ai/zen/v1/chat/completions"; Model="big-pickle";           KimiName="Big Pickle Free (Key)"; Provider="OpenCode" },
    @{ Name="Big Pickle Free (Key2)";       Env="OPENCODE_ZEN_API_KEY2"; Endpoint="https://opencode.ai/zen/v1/chat/completions"; Model="big-pickle";           KimiName="Big Pickle Free (Key2)"; Provider="OpenCode" },
    @{ Name="Nemotron 3 Ultra Free (Key3)"; Env="OPENCODE_ZEN_API_KEY3"; Endpoint="https://opencode.ai/zen/v1/chat/completions"; Model="nemotron-3-ultra-free"; KimiName="Nemotron 3 Ultra Free (Key3)"; Provider="OpenCode" },
    @{ Name="Owl Alpha Free (Key1)";        Env="OPENROUTER_API_KEY";  Endpoint="https://openrouter.ai/api/v1/chat/completions"; Model="owl-alpha";                    KimiName="Owl Alpha Free (Key1)"; Provider="OpenRouter" },
    @{ Name="Owl Alpha Free (Key2)";        Env="OPENROUTER_API_KEY2"; Endpoint="https://openrouter.ai/api/v1/chat/completions"; Model="owl-alpha";                    KimiName="Owl Alpha Free (Key2)"; Provider="OpenRouter" },
    @{ Name="North Mini Code Free (Key1)";  Env="OPENROUTER_API_KEY";  Endpoint="https://openrouter.ai/api/v1/chat/completions"; Model="cohere/north-mini-code:free";  KimiName="North Mini Code Free (Key1)"; Provider="OpenRouter" },
    @{ Name="North Mini Code Free (Key2)";  Env="OPENROUTER_API_KEY2"; Endpoint="https://openrouter.ai/api/v1/chat/completions"; Model="cohere/north-mini-code:free";  KimiName="North Mini Code Free (Key2)"; Provider="OpenRouter" },
    @{ Name="Laguna M.1 Free (Key3)";      Env="OPENROUTER_API_KEY3"; Endpoint="https://openrouter.ai/api/v1/chat/completions"; Model="poolside/laguna-m.1:free";     KimiName="Laguna M.1 Free (Key3)"; Provider="OpenRouter" },
    @{ Name="Llama 4 Scout (Groq)";         Env="GROQ_API_KEY"; Endpoint="https://api.groq.com/openai/v1/chat/completions"; Model="meta-llama/llama-4-scout-17b-16e-instruct"; KimiName="Llama 4 Scout (Groq)"; Provider="Groq" },
    @{ Name="Qwen3 32B (Groq)";             Env="GROQ_API_KEY"; Endpoint="https://api.groq.com/openai/v1/chat/completions"; Model="qwen/qwen3-32b";                         KimiName="Qwen3 32B (Groq)"; Provider="Groq" },
    @{ Name="GPT-OSS 120B (Groq)";         Env="GROQ_API_KEY"; Endpoint="https://api.groq.com/openai/v1/chat/completions"; Model="openai/gpt-oss-120b";                      KimiName="GPT-OSS 120B (Groq)"; Provider="Groq" },
    @{ Name="GPT-OSS 20B (Groq)";          Env="GROQ_API_KEY"; Endpoint="https://api.groq.com/openai/v1/chat/completions"; Model="openai/gpt-oss-20b";                       KimiName="GPT-OSS 20B (Groq)"; Provider="Groq" }
)

function Test-ModelConnection {
    param([hashtable]$Model)

    $apiKey = [Environment]::GetEnvironmentVariable($Model.Env, "Process")
    if ([string]::IsNullOrEmpty($apiKey)) {
        return @{ Success=$false; Reason="API key env var $($Model.Env) not set"; Status="SKIP" }
    }

    $headers = @{
        "Authorization" = "Bearer $apiKey"
        "Content-Type"    = "application/json"
    }
    if ($Model.Provider -eq "OpenRouter") {
        $headers["HTTP-Referer"] = "https://localhost"
        $headers["X-Title"] = "Kimi-CLI"
    }

    $body = @{
        model = $Model.Model
        messages = @(@{ role = "user"; content = "Say hi" })
        max_tokens = 10
    } | ConvertTo-Json -Depth 3 -Compress

    try {
        $response = Invoke-RestMethod -Uri $Model.Endpoint -Method Post -Headers $headers -Body $body -TimeoutSec 20 -ErrorAction Stop
        if ($response.choices -and $response.choices.Count -gt 0) {
            return @{ Success=$true; Reason="OK"; Status="200" }
        }
        if ($response.content) {
            return @{ Success=$true; Reason="OK"; Status="200" }
        }
        if ($response.error) {
            return @{ Success=$false; Reason="API error: $($response.error.message)"; Status="API_ERROR" }
        }
        return @{ Success=$false; Reason="Unexpected response"; Status="WEIRD" }
    }
    catch {
        $err = $_
        $status = "ERR"
        $reason = $err.Exception.Message
        if ($err.Exception.Response) {
            try {
                $reader = New-Object System.IO.StreamReader($err.Exception.Response.GetResponseStream())
                $reader.BaseStream.Position = 0
                $reader.DiscardBufferedData()
                $raw = $reader.ReadToEnd()
                $status = $err.Exception.Response.StatusCode.value__
                $reason = "HTTP $status : $raw"
            } catch {
                $status = $err.Exception.Response.StatusCode.value__
                $reason = "HTTP $status"
            }
        }
        return @{ Success=$false; Reason=$reason; Status=$status }
    }
}

$firstWorking = $null
$testCount = 0

foreach ($m in $testModels) {
    $testCount++
    Write-Host -NoNewline "  [$testCount/$($testModels.Count)] $($m.Name) ... "
    $result = Test-ModelConnection -Model $m
    if ($result.Success) {
        Write-Host "[WORKING]" -ForegroundColor Green
        $script:WorkingModels += $m
        if (-not $firstWorking) { $firstWorking = $m }
    } else {
        if ($result.Status -eq "SKIP") {
            Write-Host "[SKIP - no key]" -ForegroundColor DarkGray
        } else {
            Write-Host "[FAIL $($result.Status)]" -ForegroundColor Red
            Write-Host "         -> $($result.Reason.Substring(0, [Math]::Min(100, $result.Reason.Length)))" -ForegroundColor DarkGray
        }
        $script:FailedModels += $m
    }
}

# =============================================================================
# STEP 4: RESULTS
# =============================================================================

Write-Host ""
Write-Host "==============================================================="
Write-Host "  RESULTS"
Write-Host "==============================================================="
Write-Host ""

if ($script:WorkingModels.Count -eq 0) {
    Write-Host "[CRITICAL] No working models found!" -ForegroundColor Red
    exit 1
}

Write-Host "Working models ($($script:WorkingModels.Count)):"
for ($i = 0; $i -lt $script:WorkingModels.Count; $i++) {
    $wm = $script:WorkingModels[$i]
    $marker = if ($i -eq 0) { " <-- RECOMMENDED" } else { "" }
    Write-Host "  $($i+1). $($wm.KimiName) ($($wm.Provider))$marker" -ForegroundColor Green
}

Write-Host ""
Write-Host "Failed/Skipped models ($($script:FailedModels.Count)):"
foreach ($fm in $script:FailedModels) {
    Write-Host "  - $($fm.Name)" -ForegroundColor DarkGray
}

# =============================================================================
# STEP 5: LAUNCH KIMI
# =============================================================================

Write-Host ""
Write-Host "==============================================================="
Write-Host "  LAUNCHING KIMI CLI"
Write-Host "==============================================================="
Write-Host ""
Write-Host "Recommended model: $($firstWorking.KimiName)"
Write-Host ""
Write-Host "After kimi launches, type: /model"
Write-Host "Then select: $($firstWorking.KimiName)"
Write-Host ""
Write-Host "Press any key to launch kimi..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Remove-Item Env:\ANTHROPIC_BASE_URL -ErrorAction SilentlyContinue
Remove-Item Env:\ANTHROPIC_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:\ANTHROPIC_AUTH_TOKEN -ErrorAction SilentlyContinue

& $kimiPath
