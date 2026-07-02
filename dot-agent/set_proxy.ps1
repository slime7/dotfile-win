$proxy = 'http://127.0.0.1:1087'
$noProxy = 'localhost,127.0.0.1,::1,*.local,10.0.0.0/8,10.*,172.16.0.0/12,172.16.*,172.17.*,172.18.*,172.19.*,172.20.*,172.21.*,172.22.*,172.23.*,172.24.*,172.25.*,172.26.*,172.27.*,172.28.*,172.29.*,172.30.*,172.31.*,192.168.0.0/16,192.168.*'

[Environment]::SetEnvironmentVariable('HTTP_PROXY', $proxy, 'User')
[Environment]::SetEnvironmentVariable('HTTPS_PROXY', $proxy, 'User')
[Environment]::SetEnvironmentVariable('ALL_PROXY', $proxy, 'User')
[Environment]::SetEnvironmentVariable('NO_PROXY', $noProxy, 'User')
