from sys import platform

if 'linux' in platform:
    from urllib import urlencode
    import urllib2 as request
else:
    import urllib.request as request
    from urllib.parse import urlencode

"""
Auto-dial script for DSL modem model Huawei SmartAX MT882.
"""

CREDENTIALS = { # granted by ISP
    'MacWanUsrName': '44638503@speedy', 
    'MacWanPasswd': '30021332',
    }

GATEWAY_IP = '10.0.0.2'

URLS = (
    '/GenAction?%s&MacWanPasswd=30021332&ex_param1=9&MacWanBdgEn=0&MacWanIgmpEn=1&MacWanUseDns=1&MacWanGwIp=0.0.0.0&MacWanNetMask=0.0.0.0&MacWanIpAddr=0.0.0.0&prim_serv=0.0.0.0&sec_serv=0.0.0.0&MacWanVcEn=1&MacWanEncaps=3&sec_proto=0&MacWanVci=35&MacWanVpi=8&MacWanDhcpClEn=0&MacWanDefRtEn=1&MacWanNatEn=1&mtu=1492&trf_index=0&id=12&b1=Connectar' % urlencode(CREDENTIALS),
    '/GenMainPage?id=17&ex_param1=9',
    '/GenMainPage?id=20&ex_param1=17',
    )


print "Requesting connection..."
for url in URLS:
    request.urlopen("http://%s%s" % (GATEWAY_IP, url)).read()
print "Done!"
