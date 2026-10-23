$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$destination = Join-Path $root "evals\sprint3_results_historico_publico.json"
$url = "https://raw.githubusercontent.com/KaiqueKai/EnergiaLar/main/evals/sprint3_results.json"
Invoke-WebRequest -Uri $url -OutFile $destination
$data = Get-Content -LiteralPath $destination -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $data.resultados -or $data.total_casos -lt 1) {
    Remove-Item -LiteralPath $destination -Force
    throw "O arquivo histórico baixado não tem a estrutura esperada."
}
Write-Host "Histórico original da Sprint 3 baixado: $destination"
Write-Host "Total de casos registrado no arquivo: $($data.total_casos)"
Write-Host "Este arquivo é histórico e foi salvo com nome separado; não sobrescreve avaliações novas."
