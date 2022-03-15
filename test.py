import logging
import requests

def raise_assert(str):
    assert False,str
    
def create_volume(vol_name, size):

    # 1. get vpgid
    # =====================================================================================
    url_base = 'https://10.134.204.84:8080/p3api/v2/api/'
    vpg = "VG509"
    params = {"vpgName":vpg, "async": "false"}
    data   = {}
    r = requests.get(url_base + "vPG", params=params, data=data, auth=('pivot3','pivot3'), verify=False)
    print( 'get return status_code:{}'.format(r.status_code))
    if ( r.status_code == 200 ):
        r_json = r.json()
        vpgid =  r_json[0]['vpgid']
    else:
        raise_assert("vpgid was not retrievable")

    
    # 2. use vpgid to create volume
    # =====================================================================================
    print('create_volume proceed - vpgId:{}'.format(vpgid))
    params = {"vpgId" : vpgid, "async" : "false"}
    data   = {
        "name": vol_name,
        "ecLevel": "ec-1",
        "rebuildOrderPriority": "high",
        "chapEnabled": "false",
        "tierId": "1",
        "size": {
            "GiB": size
        },
        "accessControl": {
            "initiatorName": "IscsiInitiatorName",
            "access": "readwrite"
        }
    }

    print('create_volume done')
    
    r = requests.post(url_base + "vPG/vsVolume", params=params, data=data, auth=('pivot3','pivot3'), verify=False)
    print( 'post return status_code:{}'.format(r.status_code))
    if ( r.status_code == 201 and len(r.content)):
        return
    else:
        raise_assert('Got status code:{} with response:{}'.format(r.status_code, r.text))

    print('create_volume done')
    


# get vpd+id
#logging. basicConfig(filename="test.py.log", level=logging.DEBUG)
#logger = logging.getLogger(__name__)
ret = create_volume('testvol', 20)

