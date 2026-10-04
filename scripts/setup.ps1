# ──────────────────────────────────────────────────────
# Letter Buddy – Setup Script (Windows PowerShell)
# Detects GPU/VRAM, picks tier, checks/installs deps,
# pulls Ollama models, tests CUDA, sets up TTS.
# ──────────────────────────────────────────────────────

param(
    [switch]$SkipModelPull,
    [switch]$Force
)

$ErrorActionPreference = "Continue"

Write-Host "`n═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Letter Buddy – Environment Setup" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════`n" -ForegroundColor Cyan

# ── 1. System info ──────────────────────────────────
Write-Host "▶ System Information" -ForegroundColor Yellow
$cpu = (Get-WmiObject Win32_Processor).Name
$ramMB = [math]::Round((Get-WmiObject Win32_ComputerSystem).TotalPhysicalMemory / 1MB)
$os = (Get-WmiObject Win32_OperatingSystem).Caption
Write-Host "  CPU: $cpu"
Write-Host "  RAM: $ramMB MB"
Write-Host "  OS:  $os"

# ── 2. GPU detection & tier ─────────────────────────
Write-Host "`n▶ GPU Detection" -ForegroundColor Yellow
try {
    $gpuInfo = nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>&1
    if ($LASTEXITCODE -eq 0) {
        $parts = $gpuInfo -split ","
        $gpuName = $parts[0].Trim()
        $vramStr = $parts[1].Trim()
        $driver = $parts[2].Trim()
        $vramMB = [int]($vramStr -replace "[^\d]", "")

        # Determine tier
        if ($vramMB -ge 7500) { $tier = "T8" }
        elseif ($vramMB -ge 5500) { $tier = "T6" }
        elseif ($vramMB -gt 0) { $tier = "T4" }
        else { $tier = "CPU" }

        Write-Host "  GPU:    $gpuName" -ForegroundColor Green
        Write-Host "  VRAM:   $vramMB MB" -ForegroundColor Green
        Write-Host "  Driver: $driver" -ForegroundColor Green
        Write-Host "  Tier:   $tier" -ForegroundColor Green
    } else {
        $tier = "CPU"
        Write-Host "  No NVIDIA GPU detected. Using CPU tier." -ForegroundColor Red
    }
} catch {
    $tier = "CPU"
    Write-Host "  nvidia-smi not found. Using CPU tier." -ForegroundColor Red
}

# ── 3. Check Tesseract ──────────────────────────────
Write-Host "`n▶ Tesseract OCR" -ForegroundColor Yellow
$tesseractFound = $false
try {
    $tessVer = tesseract --version 2>&1 | Select-Object -First 1
    Write-Host "  Found: $tessVer" -ForegroundColor Green
    $tesseractFound = $true

    # Check language packs
    $langs = tesseract --list-langs 2>&1
    Write-Host "  Languages: $($langs -join ', ')"
    if ($langs -match "eng") {
        Write-Host "  English: ✓" -ForegroundColor Green
    } else {
        Write-Host "  English: ✗ (install with: choco install tesseract-languages)" -ForegroundColor Red
    }
} catch {
    Write-Host "  Tesseract NOT found." -ForegroundColor Red
    Write-Host "  Install with: winget install tesseract-ocr.tesseract" -ForegroundColor Yellow
    Write-Host "  Then restart this script." -ForegroundColor Yellow
}

# ── 4. Check Ollama ─────────────────────────────────
Write-Host "`n▶ Ollama LLM Runtime" -ForegroundColor Yellow
$ollamaFound = $false
try {
    $ollamaVer = ollama --version 2>&1
    Write-Host "  Found: $ollamaVer" -ForegroundColor Green
    $ollamaFound = $true
} catch {
    Write-Host "  Ollama NOT found." -ForegroundColor Red
    Write-Host "  Install from: https://ollama.ai/download" -ForegroundColor Yellow
}

# ── 5. Check eSpeak-ng ──────────────────────────────
Write-Host "`n▶ eSpeak-ng TTS" -ForegroundColor Yellow
$espeakFound = $false
try {
    $espeakVer = & "espeak-ng" --version 2>&1
    Write-Host "  Found: $espeakVer" -ForegroundColor Green
    $espeakFound = $true
} catch {
    Write-Host "  eSpeak-ng NOT found." -ForegroundColor Red
    Write-Host "  Install from: https://github.com/espeak-ng/espeak-ng/releases" -ForegroundColor Yellow
}

# ── 6. Pull LLM models ─────────────────────────────
if ($ollamaFound -and -not $SkipModelPull) {
    Write-Host "`n▶ LLM Models (Tier: $tier)" -ForegroundColor Yellow

    # Select models based on tier
    switch ($tier) {
        "T4" {
            $primaryModel = "qwen2.5:3b"
            $candidates = @("qwen2.5:3b", "llama3.2:latest")
        }
        "T6" {
            $primaryModel = "qwen2.5:7b"
            $candidates = @("qwen2.5:7b", "llama3.2:latest")
        }
        "T8" {
            $primaryModel = "qwen2.5:7b"
            $candidates = @("qwen2.5:7b", "llama3.2:latest")
        }
        default {
            $primaryModel = "qwen2.5:3b"
            $candidates = @("qwen2.5:3b")
        }
    }

    # Check which models are already pulled
    $existingModels = ollama list 2>&1
    foreach ($model in $candidates) {
        if ($existingModels -match $model.Split(":")[0]) {
            Write-Host "  $model — already pulled ✓" -ForegroundColor Green
        } else {
            Write-Host "  Pulling $model ..." -ForegroundColor Cyan
            ollama pull $model
        }
    }
}

# ── 7. Python venv ──────────────────────────────────
Write-Host "`n▶ Python Environment" -ForegroundColor Yellow
$pythonVer = python --version 2>&1
Write-Host "  Python: $pythonVer"

if (-not (Test-Path ".venv")) {
    Write-Host "  Creating virtual environment..." -ForegroundColor Cyan
    python -m venv .venv
}

Write-Host "  Activate with: .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "  Then install:  pip install -e '.[dev,eval]'" -ForegroundColor Yellow

# ── 8. Summary ──────────────────────────────────────
Write-Host "`n═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Setup Summary" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  GPU Tier:    $tier"
Write-Host "  Tesseract:   $(if ($tesseractFound) { '✓' } else { '✗ NEEDS INSTALL' })"
Write-Host "  Ollama:      $(if ($ollamaFound) { '✓' } else { '✗ NEEDS INSTALL' })"
Write-Host "  eSpeak-ng:   $(if ($espeakFound) { '✓' } else { '✗ NEEDS INSTALL' })"
Write-Host ""

if (-not $tesseractFound -or -not $ollamaFound) {
    Write-Host "  ❌ Some dependencies missing. Install them and re-run." -ForegroundColor Red
} else {
    Write-Host "  ✅ Core dependencies present. Ready for Phase 1!" -ForegroundColor Green
}
Write-Host ""
