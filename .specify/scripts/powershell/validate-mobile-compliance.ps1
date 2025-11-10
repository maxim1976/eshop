#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Mobile-First Development Validator for 日日鮮肉品專賣

.DESCRIPTION
    Validates that development follows mobile-first principles and requirements
    for the meat store e-commerce platform.

.PARAMETER Path
    Path to the project directory to validate

.PARAMETER Component
    Specific component to validate (optional)

.EXAMPLE
    .\validate-mobile-compliance.ps1 -Path "C:\path\to\project"
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$Path,
    
    [Parameter(Mandatory = $false)]
    [string]$Component = ""
)

# Import common functions
. "$PSScriptRoot\common.ps1"

function Test-MobileFirstCSS {
    param([string]$CssPath)
    
    Write-Host "🎨 Checking mobile-first CSS implementation..." -ForegroundColor Blue
    
    $violations = @()
    
    # Check for mobile-first media queries
    $cssFiles = Get-ChildItem -Path $CssPath -Recurse -Include "*.css", "*.html" -ErrorAction SilentlyContinue
    
    foreach ($file in $cssFiles) {
        $content = Get-Content -Path $file.FullName -Raw
        
        # Check for desktop-first patterns (should be mobile-first)
        if ($content -match "@media.*max-width") {
            $violations += "❌ Desktop-first media query found in $($file.Name)"
        }
        
        # Check for minimum touch target sizes
        if ($content -match "min-height:\s*[1-3]\d+px|height:\s*[1-3]\d+px") {
            $violations += "⚠️  Possible small touch targets in $($file.Name)"
        }
    }
    
    if ($violations.Count -eq 0) {
        Write-Host "✅ Mobile-first CSS patterns detected" -ForegroundColor Green
    } else {
        Write-Host "❌ Mobile-first violations found:" -ForegroundColor Red
        $violations | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
    }
    
    return $violations.Count -eq 0
}

function Test-TouchTargetSizes {
    param([string]$ProjectPath)
    
    Write-Host "👆 Checking touch target accessibility..." -ForegroundColor Blue
    
    $templateFiles = Get-ChildItem -Path "$ProjectPath\templates" -Recurse -Include "*.html" -ErrorAction SilentlyContinue
    $violations = @()
    
    foreach ($file in $templateFiles) {
        $content = Get-Content -Path $file.FullName -Raw
        
        # Check for buttons and interactive elements
        $interactiveElements = @(
            "button", "a\s+href", "input.*type=[`"']button", 
            "input.*type=[`"']submit", "\[click\]", "onclick"
        )
        
        foreach ($element in $interactiveElements) {
            if ($content -match $element) {
                # Check if element has proper sizing classes
                if ($content -notmatch "(?:h-11|h-12|h-14|p-3|p-4|py-3|py-4|min-h-\[44px\])") {
                    $violations += "⚠️  Interactive element may be too small in $($file.Name)"
                }
            }
        }
    }
    
    if ($violations.Count -eq 0) {
        Write-Host "✅ Touch targets appear adequately sized" -ForegroundColor Green
    } else {
        Write-Host "❌ Touch target issues found:" -ForegroundColor Red
        $violations | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
    }
    
    return $violations.Count -eq 0
}

function Test-MobilePerformance {
    param([string]$ProjectPath)
    
    Write-Host "⚡ Checking mobile performance considerations..." -ForegroundColor Blue
    
    $violations = @()
    
    # Check for large images without optimization
    $mediaPath = "$ProjectPath\media"
    if (Test-Path $mediaPath) {
        $largeImages = Get-ChildItem -Path $mediaPath -Recurse -Include "*.jpg", "*.png" | 
                      Where-Object { $_.Length -gt 500KB }
        
        if ($largeImages.Count -gt 0) {
            $violations += "❌ Large images found (>500KB) - may impact mobile performance"
            $largeImages | ForEach-Object { 
                $violations += "  📸 $($_.Name) - $([math]::Round($_.Length/1KB))KB"
            }
        }
    }
    
    # Check for WebP support
    $templateFiles = Get-ChildItem -Path "$ProjectPath\templates" -Recurse -Include "*.html" -ErrorAction SilentlyContinue
    $hasWebP = $false
    
    foreach ($file in $templateFiles) {
        $content = Get-Content -Path $file.FullName -Raw
        if ($content -match "\.webp|picture.*source") {
            $hasWebP = $true
            break
        }
    }
    
    if (-not $hasWebP) {
        $violations += "⚠️  No WebP image optimization detected"
    }
    
    # Check for service worker
    $serviceWorkerExists = Test-Path "$ProjectPath\static\js\sw.js" -or 
                          Test-Path "$ProjectPath\staticfiles\js\sw.js"
    
    if (-not $serviceWorkerExists) {
        $violations += "⚠️  No service worker found for offline functionality"
    }
    
    if ($violations.Count -eq 0) {
        Write-Host "✅ Mobile performance considerations look good" -ForegroundColor Green
    } else {
        Write-Host "❌ Performance issues found:" -ForegroundColor Red
        $violations | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
    }
    
    return $violations.Count -eq 0
}

function Test-ResponsiveImages {
    param([string]$ProjectPath)
    
    Write-Host "📱 Checking responsive image implementation..." -ForegroundColor Blue
    
    $templateFiles = Get-ChildItem -Path "$ProjectPath\templates" -Recurse -Include "*.html" -ErrorAction SilentlyContinue
    $violations = @()
    
    foreach ($file in $templateFiles) {
        $content = Get-Content -Path $file.FullName -Raw
        
        # Check for img tags without responsive attributes
        if ($content -match "<img[^>]*src=" -and $content -notmatch "srcset|sizes") {
            if ($file.Name -notmatch "logo|icon") {  # Exclude logos and icons
                $violations += "⚠️  Images without responsive attributes in $($file.Name)"
            }
        }
        
        # Check for proper alt attributes
        if ($content -match "<img[^>]*>" -and $content -match "<img[^>]*src=[^>]*>") {
            $imgTags = [regex]::Matches($content, "<img[^>]*>")
            foreach ($img in $imgTags) {
                if ($img.Value -notmatch "alt=") {
                    $violations += "❌ Images missing alt attributes in $($file.Name)"
                    break
                }
            }
        }
    }
    
    if ($violations.Count -eq 0) {
        Write-Host "✅ Responsive image implementation looks good" -ForegroundColor Green
    } else {
        Write-Host "❌ Responsive image issues found:" -ForegroundColor Red
        $violations | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
    }
    
    return $violations.Count -eq 0
}

function Test-MobileFriendlyForms {
    param([string]$ProjectPath)
    
    Write-Host "📝 Checking mobile-friendly form implementation..." -ForegroundColor Blue
    
    $templateFiles = Get-ChildItem -Path "$ProjectPath\templates" -Recurse -Include "*.html" -ErrorAction SilentlyContinue
    $violations = @()
    
    foreach ($file in $templateFiles) {
        $content = Get-Content -Path $file.FullName -Raw
        
        # Check for appropriate input types
        if ($content -match "input.*type=[`"']text[`"'].*email|input.*type=[`"']text[`"'].*phone") {
            $violations += "⚠️  Consider using appropriate input types (email, tel) in $($file.Name)"
        }
        
        # Check for minimum input height
        if ($content -match "input" -and $content -notmatch "h-11|h-12|py-3|py-4") {
            $violations += "⚠️  Form inputs may be too small for mobile in $($file.Name)"
        }
        
        # Check for autocomplete attributes
        if ($content -match "input.*type=[`"']email[`"']" -and $content -notmatch "autocomplete") {
            $violations += "⚠️  Email inputs missing autocomplete attributes in $($file.Name)"
        }
    }
    
    if ($violations.Count -eq 0) {
        Write-Host "✅ Mobile-friendly form implementation detected" -ForegroundColor Green
    } else {
        Write-Host "❌ Form optimization issues found:" -ForegroundColor Red
        $violations | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
    }
    
    return $violations.Count -eq 0
}

function Test-TaiwanMobileFeatures {
    param([string]$ProjectPath)
    
    Write-Host "🇹🇼 Checking Taiwan mobile market features..." -ForegroundColor Blue
    
    $violations = @()
    
    # Check for Traditional Chinese language support
    $templateFiles = Get-ChildItem -Path "$ProjectPath\templates" -Recurse -Include "*.html" -ErrorAction SilentlyContinue
    $hasTraditionalChinese = $false
    
    foreach ($file in $templateFiles) {
        $content = Get-Content -Path $file.FullName -Raw
        if ($content -match "[\u4e00-\u9fff]") {  # Chinese characters
            $hasTraditionalChinese = $true
            break
        }
    }
    
    if (-not $hasTraditionalChinese) {
        $violations += "⚠️  No Traditional Chinese content detected"
    }
    
    # Check for mobile payment integration references
    $paymentFiles = Get-ChildItem -Path $ProjectPath -Recurse -Include "*.py", "*.html" -ErrorAction SilentlyContinue
    $hasMobilePayments = $false
    
    foreach ($file in $paymentFiles) {
        $content = Get-Content -Path $file.FullName -Raw
        if ($content -match "Apple Pay|Google Pay|Line Pay|taiwan.*payment") {
            $hasMobilePayments = $true
            break
        }
    }
    
    if (-not $hasMobilePayments) {
        $violations += "⚠️  No Taiwan mobile payment methods detected"
    }
    
    if ($violations.Count -eq 0) {
        Write-Host "✅ Taiwan mobile features implemented" -ForegroundColor Green
    } else {
        Write-Host "❌ Taiwan mobile feature gaps:" -ForegroundColor Red
        $violations | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
    }
    
    return $violations.Count -eq 0
}

# Main execution
function Main {
    Write-Host "🥩 日日鮮肉品專賣 Mobile-First Validation" -ForegroundColor Magenta
    Write-Host "=" * 50
    
    if (-not (Test-Path $Path)) {
        Write-Host "❌ Project path not found: $Path" -ForegroundColor Red
        exit 1
    }
    
    $results = @()
    
    # Run all mobile validation tests
    $results += Test-MobileFirstCSS -CssPath "$Path\templates"
    $results += Test-TouchTargetSizes -ProjectPath $Path
    $results += Test-MobilePerformance -ProjectPath $Path
    $results += Test-ResponsiveImages -ProjectPath $Path
    $results += Test-MobileFriendlyForms -ProjectPath $Path
    $results += Test-TaiwanMobileFeatures -ProjectPath $Path
    
    Write-Host ""
    Write-Host "📊 Mobile-First Compliance Summary" -ForegroundColor Cyan
    Write-Host "=" * 40
    
    $passedTests = ($results | Where-Object { $_ -eq $true }).Count
    $totalTests = $results.Count
    $score = [math]::Round(($passedTests / $totalTests) * 100)
    
    Write-Host "Score: $passedTests/$totalTests tests passed ($score%)" -ForegroundColor $(if ($score -ge 80) { "Green" } else { "Yellow" })
    
    if ($score -ge 90) {
        Write-Host "🎉 Excellent mobile-first implementation!" -ForegroundColor Green
    } elseif ($score -ge 70) {
        Write-Host "👍 Good mobile implementation with room for improvement" -ForegroundColor Yellow
    } else {
        Write-Host "⚠️  Mobile implementation needs significant work" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "💡 Next Steps:" -ForegroundColor Blue
    Write-Host "1. Address any ❌ critical issues found above"
    Write-Host "2. Consider ⚠️  warnings for enhanced mobile experience"
    Write-Host "3. Test on real devices (iOS Safari, Android Chrome)"
    Write-Host "4. Run Lighthouse mobile performance audit"
    
    return $score -ge 70
}

# Execute main function
if ($MyInvocation.InvocationName -ne '.') {
    $success = Main
    exit $(if ($success) { 0 } else { 1 })
}