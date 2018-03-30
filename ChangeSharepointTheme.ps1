#!/usr/bin/env powershell
function wait-IE{while($ie.Busy) { Start-Sleep -Milliseconds 100 }}

function script:Filter-Windows(){
    Param(
        [Parameter(Mandatory=$true,HelpMessage='Windows required to filter')][__ComObject]$windows, 
        [Parameter(Mandatory=$true,HelpMessage='Target handle required to filter')][int]$handle)
    return $windows | Where-Object{$_.HWND -eq $handle}
}

function script:Connect-IExplorer() {
    
    param(
        [Parameter(Mandatory=$true,HelpMessage='Handle required to find window')][int]$HWND)
    
    $objShellApp = New-Object -ComObject Shell.Application
    
    try {
        
        $EA = $ErrorActionPreference
        $ErrorActionPreference = 'Stop'
        
        $objNewIE = Filter-Windows -windows $objShellApp.Windows() -handle $HWND
        
        $objNewIE.Visible = $true
        
    } catch {
        
        #it may happen, that the Shell.Application does not find the window in a timely-manner, therefore quick-sleep and try again
        
        Write-Verbose -Message 'Waiting for page to be loaded ...'
        
        Start-Sleep -Milliseconds 500
        
        try {
            
            $objNewIE = Filter-Windows -windows $objShellApp.Windows() -handle $HWND
            
            #$objNewIE.Visible = $true
            
        } catch {
            
            Write-Verbose -Message 'Could not retreive the -com Object InternetExplorer. Aborting.'
            
            $objNewIE = $null
            
        }    
        
    } finally {
        
        $ErrorActionPreference = $EA
        
        $objShellApp = $null
        
    }
    
    return $objNewIE
    
}

$HWND = ($ie = New-Object -ComObject InternetExplorer.Application).HWND

#$ie.Visible = $true

$ie.Silent = $true

$ie.Navigate('https://sharepointsite.com/start.aspx#/_layouts/15/designgallery.aspx')

$ie = Connec-IExplorer -HWND $HWND

wait-IE

Start-Sleep -Seconds 5

$doc = $ie.Document



$nodes = $doc.getElementsByTagName('div') | Where-Object{$_.ClassName -eq 'ms-designgallery-item'}

$node = $nodes[$(Get-Random -Minimum 0 -Maximum $nodes.Length)]

$node.click()

wait-IE

Start-Sleep -Seconds 5

$node = $doc.getElementsByTagName('a') | Where-Object{$_.Title -eq 'Try it out'}

$node.click()

wait-IE

Start-Sleep -Seconds 20

$doc.getElementById('btnOk').click()