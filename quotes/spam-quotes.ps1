
# Script to get quotes, pick one, remote TTS the quote on target machine
# using PoSH as we'll try PSRemoting to do RPC on target machine

$tag = 'nihilism'

# These were manually set by looking at the website - later we should set dynamically
$pages = 12
$totalQuotes = 350
Get-ChildItem -Path . -Filter scraped-*.txt | ForEach-Object { Remove-Item $_.FullName -Force }

python .\goodreads-scraper.py -t $tag -p $pages -q $totalQuotes

$quoteText = Get-Content ".\scraped-$tag.txt" | Sort-Object { get-random } | Select-Object -First 1

# TODO: make scriptblock not string
$command = "
    Add-Type –AssemblyName System.Speech
    `$SpeechSynthesizer = New-Object –TypeName System.Speech.Synthesis.SpeechSynthesizer
    `$SpeechSynthesizer.Speak($quoteText)
    "
# Enable-PSRemoting -Force
# Set-Service WinRM -StartMode Automatic
# http://www.sirchristian.net/blog/2013/03/11/using-powershell-remoting-over-the-internet-for-one-click-build-and-deploy/
# makecert.exe -r -pe -n "CN=collectedit.com" `
# -eku 1.3.6.1.5.5.7.3.1 -ss my -sr localmachine -sky exchange`
# -sp "Microsoft RSA SChannel Cryptographic Provider" -sy 12
# ls Cert:\LocalMachine\My
# winrm create `
# winrm/config/Listener?Address=*+Transport=HTTPS`@`{Hostname=`"`collectedit.com`"`
# ;CertificateThumbprint=`"`XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`"`}
# $so = New-PSSessionOption -SkipCACheck # skip certificate authority check
# Enter-PSSession localhost -UseSSL -SessionOption $so # note the "UseSSL"
Invoke-Command -SessionOption $so -UseSSL -ComputerName $Servers -Credential $remotecreds -ArgumentList ($Config) -ScriptBlock 