$repos = @(
    # Core Top 10 series
    <#"Top10",
    "API-Security",
    "www-project-top-10-for-large-language-model-applications",
    "www-project-top-10-ci-cd-security-risks",
    "www-project-machine-learning-security-top-10",
    
    # Verification standards
    "ASVS",
    "AISVS",
    "www-project-proactive-controls",
    
    # Testing & code review
    "wstg",
    "CodeReviewGuide",
    "www-project-ai-testing-guide",
    
    # Reference content
    "CheatSheetSeries",
    "DevGuide",
    "www-project-secure-coding-practices-quick-reference-guide",
    "www-community",
    #>
    # AI/ML security
    "GenAI-Security-Project/GenAI-Agent-Security-Initiative",
    "GenAI-Security-Project/GenAI-LLM-Top10"
    <#
    # Threat modeling
    "www-project-threat-modeling-playbook",
    
    # Cloud & modern
    "www-project-cloud-native-application-security-top-10",
    
    # Specialized (for breadth)
    "www-project-mobile-top-10",
    "www-project-kubernetes-top-ten"#>
)

$successful = @()
$failed = @()

foreach ($repo in $repos) {
    Write-Host "`nCloning $repo..." -ForegroundColor Cyan
    
    # Check if already cloned
    if (Test-Path $repo) {
        Write-Host "  ⏭️  Already exists, pulling latest..." -ForegroundColor Yellow
        Push-Location $repo
        git pull --quiet
        Pop-Location
        $successful += $repo
        continue
    }
    
    # Clone
    $result = git clone --depth 1 "https://github.com/$repo.git" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Success" -ForegroundColor Green
        $successful += $repo
    } else {
        Write-Host "  ❌ Failed: $result" -ForegroundColor Red
        $failed += $repo
    }
}

# Summary
Write-Host "`n" -NoNewline
Write-Host "=" * 60
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "  ✅ Successful: $($successful.Count)" -ForegroundColor Green
Write-Host "  ❌ Failed: $($failed.Count)" -ForegroundColor Red

if ($failed.Count -gt 0) {
    Write-Host "`nFailed repos:" -ForegroundColor Red
    $failed | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
}

Write-Host "`nTotal disk usage:" -ForegroundColor Cyan
$size = (Get-ChildItem -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host ("  {0:N1} MB" -f $size)
