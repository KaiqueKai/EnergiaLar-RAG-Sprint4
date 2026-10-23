$ErrorActionPreference = "Stop"
# Os dois links abaixo são os links de Download expostos na página oficial GoodWe Brasil HCA G2.
# O manual é obrigatório. A lista de compatibilidade é uma fonte oficial complementar.
$kbDir = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\data\knowledge_base"))
New-Item -ItemType Directory -Force -Path $kbDir | Out-Null
$downloads = @(
    @{
        Uri = "https://br.goodwe.com/Api/downloadFile?id=2496&mid=60&type=2"
        FileName = "00_manual_oficial_goodwe_hca_g2_en.pdf"
        Label = "Manual oficial GoodWe HCA G2 (EN)"
        Required = $true
    },
    @{
        Uri = "https://br.goodwe.com/Api/downloadFile?id=4535&mid=60&type=2"
        FileName = "00b_compatibilidade_goodwe_ev_hca_g2_en.pdf"
        Label = "Lista oficial de compatibilidade de carregadores e inversores (EN)"
        Required = $false
    }
)
foreach ($item in $downloads) {
    $dest = Join-Path $kbDir $item.FileName
    $temp = "$dest.download.tmp"
    Write-Host "Baixando: $($item.Label)"
    try {
        Invoke-WebRequest -Uri $item.Uri -OutFile $temp -UseBasicParsing
        $bytes = [System.IO.File]::ReadAllBytes($temp)
        if ($bytes.Length -lt 10000 -or [System.Text.Encoding]::ASCII.GetString($bytes[0..4]) -ne "%PDF-") {
            throw "O arquivo recebido não parece ser PDF válido."
        }
        Move-Item -LiteralPath $temp -Destination $dest -Force
        Write-Host "OK: $dest ($($bytes.Length) bytes)."
    } catch {
        Remove-Item -LiteralPath $temp -ErrorAction SilentlyContinue
        if ($item.Required) {
            throw "Não foi possível baixar o manual oficial obrigatório. Abra https://br.goodwe.com/download-hca-g2-series, localize 'GW_HCA G2_User Manual-EN' e salve-o como '$dest'. Detalhe: $($_.Exception.Message)"
        }
        Write-Warning "A fonte complementar não foi baixada automaticamente: $($item.Label). Abra https://br.goodwe.com/download-hca-g2-series e procure o arquivo correspondente. O manual principal foi mantido; detalhe: $($_.Exception.Message)"
    }
}
Write-Host "Download concluído. Confira os arquivos em: $kbDir"
Write-Host "Próximo passo: .\.venv\Scripts\python.exe -m src.rag.build_index --force"
