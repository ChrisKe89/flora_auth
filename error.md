(.venv) PS C:\Dev\flora_auth>    pip install -r requirements.txt
>> $env:PLAYWRIGHT_BROWSERS_PATH = "$PWD\.pw-browsers"
>> python -m playwright install chromium
Requirement already satisfied: playwright==1.48.0 in c:\dev\flora_auth\.venv\lib\site-packages (from -r requirements.txt (line 1)) (1.48.0)
Requirement already satisfied: greenlet==3.1.1 in c:\dev\flora_auth\.venv\lib\site-packages (from playwright==1.48.0->-r requirements.txt (line 1)) (3.1.1)
Requirement already satisfied: pyee==12.0.0 in c:\dev\flora_auth\.venv\lib\site-packages (from playwright==1.48.0->-r requirements.txt (line 1)) (12.0.0)
Requirement already satisfied: typing-extensions in c:\dev\flora_auth\.venv\lib\site-packages (from pyee==12.0.0->playwright==1.48.0->-r requirements.txt (line 1)) (4.15.0)

[notice] A new release of pip is available: 25.1.1 -> 25.3
[notice] To update, run: python.exe -m pip install --upgrade pip
Downloading Chromium 130.0.6723.31 (playwright build v1140) from <https://playwright.azureedge.net/builds/chromium/1140/chromium-win64.zip>
Error: self-signed certificate in certificate chain
    at TLSSocket.onConnectSecure (node:_tls_wrap:1677:34)
    at TLSSocket.emit (node:events:519:28)
    at TLSSocket._finishInit (node:_tls_wrap:1076:8)
    at ssl.onhandshakedone (node:_tls_wrap:862:12) {
  code: 'SELF_SIGNED_CERT_IN_CHAIN'
}
Downloading Chromium 130.0.6723.31 (playwright build v1140) from <https://playwright-akamai.azureedge.net/builds/chromium/1140/chromium-win64.zip>
Error: self-signed certificate in certificate chain
    at TLSSocket.onConnectSecure (node:_tls_wrap:1677:34)
    at TLSSocket.emit (node:events:519:28)
    at TLSSocket._finishInit (node:_tls_wrap:1076:8)
    at ssl.onhandshakedone (node:_tls_wrap:862:12) {
  code: 'SELF_SIGNED_CERT_IN_CHAIN'
}
Downloading Chromium 130.0.6723.31 (playwright build v1140) from <https://playwright-verizon.azureedge.net/builds/chromium/1140/chromium-win64.zip>
Error: self-signed certificate in certificate chain
    at TLSSocket.onConnectSecure (node:_tls_wrap:1677:34)
    at TLSSocket.emit (node:events:519:28)
    at TLSSocket._finishInit (node:_tls_wrap:1076:8)
    at ssl.onhandshakedone (node:_tls_wrap:862:12) {
  code: 'SELF_SIGNED_CERT_IN_CHAIN'
}
Failed to install browsers
Error: Failed to download Chromium 130.0.6723.31 (playwright build v1140), caused by
Error: Download failure, code=1
    at ChildProcess.<anonymous> (C:\Dev\flora_auth\.venv\Lib\site-packages\playwright\driver\package\lib\server\registry\browserFetcher.js:91:16)
    at ChildProcess.emit (node:events:519:28)
    at ChildProcess._handle.onexit (node:internal/child_process:294:12)


# 1) Temporarily allow Node to accept your corp MITM cert

$env:NODE_TLS_REJECT_UNAUTHORIZED = "0"

# 2) Keep browsers in-repo (your preference)

$env:PLAYWRIGHT_BROWSERS_PATH = "$PWD\.pw-browsers"

# 3) Install Chromium

python -m playwright install chromium

# 4) (Important) Remove the insecure override for the rest of your session

Remove-Item Env:\NODE_TLS_REJECT_UNAUTHORIZED
