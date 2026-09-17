# Native raster conversion of the existing mesh-derived SVG subset; no model edits.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
function SvgColor($value, $opacity = 1.0) {
    $color = [System.Drawing.ColorTranslator]::FromHtml($value)
    return [System.Drawing.Color]::FromArgb([int](255 * $opacity), $color)
}
function DrawNode($node, $graphics, $document, $width, $height) {
    switch ($node.LocalName) {
        'defs' { return }
        'rect' {
            $x = 0.0; $y = 0.0
            if ($node.HasAttribute('x')) { $x = [single]$node.GetAttribute('x') }
            if ($node.HasAttribute('y')) { $y = [single]$node.GetAttribute('y') }
            $w = if ($node.GetAttribute('width') -eq '100%') { $width } else { [single]$node.GetAttribute('width') }
            $h = if ($node.GetAttribute('height') -eq '100%') { $height } else { [single]$node.GetAttribute('height') }
            $brush = [System.Drawing.SolidBrush]::new((SvgColor $node.GetAttribute('fill')))
            $graphics.FillRectangle($brush, [single]$x, [single]$y, [single]$w, [single]$h)
            $brush.Dispose(); return
        }
        { $_ -in 'polygon','polyline' } {
            [System.Drawing.PointF[]]$points = @($node.GetAttribute('points').Trim() -split '\s+' | ForEach-Object {
                $xy = $_ -split ','
                [System.Drawing.PointF]::new([single]$xy[0], [single]$xy[1])
            })
            $fill = $node.GetAttribute('fill')
            if ($fill -and $fill -ne 'none') {
                $brush = [System.Drawing.SolidBrush]::new((SvgColor $fill))
                $graphics.FillPolygon($brush, $points); $brush.Dispose()
            }
            $stroke = $node.GetAttribute('stroke')
            if ($stroke -and $stroke -ne 'none') {
                $opacity = 1.0
                if ($node.HasAttribute('stroke-opacity')) { $opacity = [double]$node.GetAttribute('stroke-opacity') }
                $pen = [System.Drawing.Pen]::new((SvgColor $stroke $opacity), [single]$node.GetAttribute('stroke-width'))
                if ($node.GetAttribute('stroke-linecap') -eq 'round') {
                    $pen.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
                    $pen.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
                }
                if ($node.GetAttribute('stroke-linejoin') -eq 'round') { $pen.LineJoin = [System.Drawing.Drawing2D.LineJoin]::Round }
                if ($node.LocalName -eq 'polygon') { $graphics.DrawPolygon($pen, $points) }
                else { $graphics.DrawLines($pen, $points) }
                $pen.Dispose()
            }
            return
        }
        'text' {
            $size = [single]$node.GetAttribute('font-size')
            $font = [System.Drawing.Font]::new('Arial', $size, [System.Drawing.FontStyle]::Regular, [System.Drawing.GraphicsUnit]::Pixel)
            $fill = $node.GetAttribute('fill'); if (-not $fill) { $fill = '#000000' }
            $brush = [System.Drawing.SolidBrush]::new((SvgColor $fill))
            $format = [System.Drawing.StringFormat]::GenericTypographic.Clone()
            if ($node.GetAttribute('text-anchor') -eq 'middle') { $format.Alignment = [System.Drawing.StringAlignment]::Center }
            $ascent = $font.FontFamily.GetCellAscent($font.Style) * $size / $font.FontFamily.GetEmHeight($font.Style)
            $graphics.DrawString($node.InnerText, $font, $brush, [System.Drawing.PointF]::new([single]$node.GetAttribute('x'), ([single]$node.GetAttribute('y') - $ascent)), $format)
            $font.Dispose(); $brush.Dispose(); $format.Dispose(); return
        }
    }
    $state = $graphics.Save()
    if ($node.LocalName -eq 'g' -and $node.HasAttribute('clip-path')) {
        $clip = $document.SelectSingleNode("//*[local-name()='clipPath']/*[local-name()='rect']")
        $graphics.SetClip([System.Drawing.RectangleF]::new([single]$clip.x, [single]$clip.y, [single]$clip.width, [single]$clip.height))
    }
    foreach ($child in $node.ChildNodes) {
        if ($child -is [System.Xml.XmlElement]) { DrawNode $child $graphics $document $width $height }
    }
    $graphics.Restore($state)
}
Get-ChildItem -LiteralPath $PSScriptRoot -Filter 'plan_v03_*.svg' | ForEach-Object {
    [xml]$document = Get-Content -LiteralPath $_.FullName -Raw
    $width = [int]$document.DocumentElement.width
    $height = [int]$document.DocumentElement.height
    $bitmap = [System.Drawing.Bitmap]::new($width, $height)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    DrawNode $document.DocumentElement $graphics $document $width $height
    $output = [System.IO.Path]::ChangeExtension($_.FullName, '.png')
    $bitmap.Save($output, [System.Drawing.Imaging.ImageFormat]::Png)
    $graphics.Dispose(); $bitmap.Dispose()
    Write-Output $output
}
