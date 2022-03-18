__author__ = 'Brian Auld'

from oslo_config import cfg
from oslo_log import log as logging
from cinder import interface
from cinder.volume import driver
import requests
import json

LOG = logging.getLogger(__name__)
CONF = cfg.CONF
ENABLE_TRACE = False

volume_opts = [
    cfg.StrOpt('quantum_api_endpoint',
               default='https://10.134.204.84:8080',
               help='the api endpoint at which the quantum storage system sits')
]

CONF = cfg.CONF
CONF.register_opts(volume_opts)

@interface.volumedriver
class QuantumDriver(driver.VolumeDriver):

    VERSION = '3.0.0'


    def __init__(self, *args, **kwargs):
        super(QuantumDriver, self).__init__(*args, **kwargs)
        self.configuration.append_config_values(volume_opts)
        self.endpoint = self.configuration.safe_get('quantum_api_endpoint')

        self.vpg_name      = "VG509"
        self.p3api_v1 = "https://10.134.204.84:8443/p3api/v1/"
        self.p3api_v2 = "https://10.134.204.84:8080/p3api/v2/api/"
        # we should be able to set this via our api but it's troublesome
        self.initiator_iqn = "iqn.2005-03.org.open-iscsi:53f3e15775f5"
        self.single_poc_target_portal = "10.134.22.21"
        
    def raise_assert(self, str):
        assert False,str

    def logmsg(self, string):
        LOG.info('qmco_api ' + string)

    def do_setup(self, context):
        params = {"vpgName":self.vpg_name, "async": "false"}
        data   = {}
        r = requests.get(self.p3api_v2 + "vPG", params=params, data=data, auth=('pivot3','pivot3'), verify=False)
        self.print_requests_response("qmco api Get VPG Info", r)
        if ( r.status_code == 200 ):
            r_json = r.json()
            self.vpgid =  r_json[0]['vpgid']
        else:
            self.raise_assert("vpgid was not retrievable")

    def remove_export(self, context, volume):

        vol_str = 'remove_export ->'        + \
            ' name: ' + volume['name']      + \
            ' id: '   + volume['id']        + \
            ' size: ' + str(volume['size'])
        self.logmsg(vol_str)


    def create_volume(self, volume):
        
        vol_str = 'create_volume start ->'        + \
            ' name: ' + volume['display_name']      + \
            ' id: '   + volume['id']        + \
            ' size: ' + str(volume['size']) 
        self.logmsg(vol_str)

        # 2. use vpgid to create volume
        # =====================================================================================
        self.logmsg('create_volume proceed - vpgId:{} volume:{}'.format(self.vpgid, volume['display_name']))
        params = {"vpgId" : self.vpgid, "async" : "false"}
        data   = {
            "name": volume['display_name'],
            "ecLevel": "ec-1",
            "rebuildOrderPriority": "high",
            "chapEnabled": "false",
            "tierId": "1",
            "size": {
                "GiB": volume['size']
            },
            "accessControl": {
                "initiatorName": self.initiator_iqn,
                "access": "readwrite"
            }
        }
        r = requests.post(self.p3api_v2 + "vPG/vsVolume", params=params, json=data, auth=('pivot3','pivot3'), verify=False)
        self.print_requests_response("qmco api create volume", r)
        if ( r.status_code == 201 and len(r.content)):
            self.logmsg('create_volume done')
            return
        else:
            self.raise_assert('Got status code:{} with response:{}'.format(r.status_code, r.text))
            self.logmsg('create_volume done error')

    def delete_volume(self, volume):
        vol_str = 'delete_volume start ->'        + \
            ' name: ' + volume['display_name']      + \
            ' id: '   + volume['id']        + \
            ' size: ' + str(volume['size']) 
        self.logmsg(vol_str)

        # 1. delete volume
        # =====================================================================================
        self.logmsg('delete proceed - vpgId:{}'.format(vpgid))
        params = {"vpgId" : self.vpgid, "async" : "false", "volumeName" : volume['display_name']}
        data   = {}
        r = requests.delete(self.p3api_v2 + "vPG/vsVolume", params=params, json=data, auth=('pivot3','pivot3'), verify=False)
        self.print_requests_response("qmco api Delete Volume", r)
        if ( r.status_code == 200 ):
            self.logmsg('delete_volume done')
            return
        else:
            self.raise_assert('Got status code:{} with response:{}'.format(r.status_code, r.text))
            self.logmsg('create_volume done error')

    def create_export(self, context, volume, connector):
        vol_str = 'create export start ->'        + \
            ' name: ' + volume['display_name']      + \
            ' id: '   + volume['id']        + \
            ' size: ' + str(volume['size'])
        self.logmsg(vol_str)
        print('context   -> {}'.format(context))
        print('volume    -> {}'.format(volume))
        print('connector -> {}'.format(connector))
        self.logmsg("create export done")
        
    def update_volume(self, volume):
        self.logmsg('update/n')

    def get_vol_by_id(self, volume):
        self.logmsg('get vol by id/n')

    def get_vols(self):
        self.logmsg('get vols/n')

    def attach_volume(self, context, volume, instance_uuid, host_name, mountpoint):
        
        print('qmco api attach_volume context:{}'.format(context))
        print('qmco api attach_volume volume:{}'.format(volume))
        print('qmco api attach_volume instance_uuid:{}'.format(instance_uuid))
        print('qmco api attach_volume host_name:{}'.format(host_name))
        print('qmco api attach_volume mountpoint:{}'.format(mountpoint))
        self.logmsg('attach_volume done/n')

    def check_for_setup_error(self):
        self.logmsg('check for setup error/n')

    def clone_image(self):
        self.logmsg('clone/n')

    def copy_image_to_volume(self):
        self.logmsg('img to vol/n')

    def copy_volume_to_image(self):
        self.logmsg('vol to img/n')

    def detach_volume(self):
        self.logmsg('detach vol /n')

    def extend_volume(self):
        self.logmsg('extend vol /n')

    def get_volume_stats(self, refresh=False):
         ret = {
             'volume_backend_name': 'quantum',
             'vendor_name': 'bar',
             'driver_version': '3.0.0',
             'storage_protocol': 'iSCSI',
             'total_capacity_gb': 42,
             'free_capacity_gb': 42
         }
         self.logmsg('updating backend stats')
         return ret

    def initialize_connection(self, volume, connector):

        vol_str = 'initialize_connection start ->'        + \
            ' name: ' + volume['display_name']      + \
            ' id: '   + volume['id']        + \
            ' size: ' + str(volume['size'])
        self.logmsg(vol_str)
        print('volume    -> {}'.format(volume))
        print('connector -> {}'.format(connector))

        # 1. get volume_id
        # =====================================================================================
        p3volume = self.get_volume_details(volume)

        # 2. set the initiator name ...
        #
        # **** this was hard-code at volume create. should really be doing this from the connector['initiator'] info
        # ==========================================================================================================
        # see v1 api call notes below
        #params = {"vpgId":vpgid, "volumeName":volume['display_name'], "initiatorName":connector['initiator'],"async": "false", }
        # url    = self.p3api_v1 + "array/" +  self.vpgid + "/volume/" + p3volume['id'] + "/accessControl/addAccessControl"
        # data   = {"access":"Read/Write", "chapsecret":"", "initiatorname":connector['initiator']}
        # r = requests.post(url, data=data, auth=('pivot3','pivot3'), verify=False)
        # #self.print_requests_response("qmco api Set Initiator Name", r)
        # self.logmsg( 'get return status_code:{}'.format(r.status_code))
        # if ( r.status_code == 200 ):
        #     r_json = r.json()
        #     self.logmsg( 'POST response content follows' )
        #     print(r_json)
        # else:
        #     self.raise_assert("vpgid was not retrievable")
        # self.logmsg('ready to complete volume info for vol:{}'.format(p3volumne))
        # self.logmsg("initialize_connection done")
        # p3volume = self.get_volume_details(volume)
        
        conn_info =  {'driver_volume_type': 'iscsi',
                      'data': {'target_discovered': False,
                               'target_portal': self.single_poc_target_portal,
                               'target_iqn': p3volume['iscsiTargetName'],
                               'target_lun': 0,
                               'volume_id': p3volume['id'],
                               # 'auth_method': 'CHAP',
                               # 'auth_username': 'cAeghKukHVNeC7eJzp2b',
                               # 'auth_password': '8kU8FoRQWXJYE7ku',
                               'encrypted': False}}
        return conn_info
                                                                  
    def terminate_connection(self, volume, connector, force):
        self.logmsg('terminate_connection enter/n')
        print('qmco api termination_connection volume:{}'.format(volume))
        print('qmco api termination_connection connector:{}'.format(connector))
        print('qmco api termination_connection force:{}'.format(force))
        self.logmsg('terminate_connection done/n')
        


    # this help is not necessary if we can save the vol_id locally
    def get_volume_details(self, volume):
        params = {"vpgId":self.vpgid, "volumeName":volume['display_name'], "async": "false"}
        data   = {}
        r = requests.get(self.p3api_v2 + "vPG/vsVolume", params=params, data=data, auth=('pivot3','pivot3'), verify=False)
        self.print_requests_response("qmco api Get Volume Info", r)
        if ( r.status_code == 200 ):
            r_json = r.json()
            return  r_json[0]
        else:
            self.raise_assert("vpgid was not retrievable")
     
    def print_requests_response(self, action, response):
        print(action)
        pretty_json = json.loads(response.text)
        print(json.dumps(pretty_json, indent=2))

# A. Volume field
# ===========================================================================================================
# ===========================================================================================================
#         _name_id=None,
#         admin_metadata={},
#         attach_status='detached',
#         availability_zone='nova',
#         bootable=False,
#         cluster=<?>,
#         cluster_name=None,
#         consistencygroup=<?>,
#         consistencygroup_id=None,
#         created_at=2022-03-15T17:10:28Z,
#         deleted=False,deleted_at=None,
#         display_description=None,
#         display_name='testvol2',
#         ec2_id=None,
#         encryption_key_id=None,
#         glance_metadata=<?>,
#         group=<?>,
#         group_id=None,
#         host='den-bauld-dstack@quantum#quantum',
#         id=84d6b74d-6d82-42f1-a69a-45bf85cfd8a5,
#         launched_at=None,
#         metadata={},
#         migration_status=None,
#         multiattach=False,
#         previous_status=None,
#         project_id='22759826927a4c0dad8bf00dedd5b91f',
#         provider_auth=None,
#         provider_geometry=None,
#         provider_id=None,
#         provider_location=None,
#         replication_driver_data=None,
#         replication_extended_status=None,
#         replication_status=None,
#         scheduled_at=2022-03-15T17:10:28Z,
#         service_uuid=None,
#         shared_targets=True,
#         size=20,
#         snapshot_id=None,
#         snapshots=<?>,
#         source_volid=None,
#         status='creating',
#         terminated_at=None,
#         updated_at=2022-03-15T17:10:28Z,
#         use_quota=True,
#         user_id='fa12b8237e354d45a91a4ede38ae017c',
#         volume_attachment=VolumeAttachmentList,
#         volume_type=VolumeType(4709615a-fd13-49e2-b5da-fe6367682825),
#         volume_type_id=4709615a-fd13-49e2-b5da-fe6367682825)



# B. conn_info return from initialize_connection
# ===========================================================================================================
# ===========================================================================================================
# # conn_info return to caller
#
# {'driver_volume_type': 'iscsi',
#  'data': {'target_discovered': False,
#           'target_portal': '10.134.204.85:3260',
#           'target_iqn': 'iqn.2010-10.org.openstack:volume-348e5c49-41f2-4896-83f0-853588889fd5',
#           'target_lun': 0,
#           'volume_id': '348e5c49-41f2-4896-83f0-853588889fd5',
#           'auth_method': 'CHAP',
#           'auth_username': 'cAeghKukHVNeC7eJzp2b',
#           'auth_password': '8kU8FoRQWXJYE7ku',
#           'encrypted': False}}



# C. connector...
# ===========================================================================================================
# ===========================================================================================================
# {'platform': 'x86_64',
#  'os_type': 'linux',
#  'ip': '10.134.6.33',
#  'host': 'devstack-vm-vg509-2',
#  'multipath': False,
#  'initiator': 'iqn.2005-03.org.open-iscsi:4aa7c12387f9',
#  'do_local_attach': False,
#  'uuid': '7c89a707-98c2-4b5a-ab15-9a035052f55e',
#  'system uuid': '0a352442-53ee-eb25-5778-d8d846ae6122',
#  'mountpoint': '/dev/vdb'}

# "vpgid": "600176c27bacb2c5c77c9cbe2916c172",



# D. v1 api call to update initiator access
# ===========================================================================================================
# ===========================================================================================================
# v1 api call for adding new host access
# **** you cannot modify, you can only remove or add
# **** the DELETE shown below is for removing the original accessControl field set a volume create time, since the attach comes later....
# POST https://10.134.204.84:8443/p3api/v1/array/600176c27bacb2c5c77c9cbe2916c172/volume/600176c311aa3cf3bbac5d2a2916c172/accessControl/addAccessControl
# {
#     "access":"Read/Write",
#     "chapsecret":"",
#     "initiatorname":"craigtest"
# }

# DELETE https://10.134.204.84:8443/p3ap1/v1/array/600176c27bacb2c5c77c9cbe2916c172/volume/600176c311aa3cf3bbac5d2a2916c172/accessControl/deleteAccessControl
# {
#    "initiatorname":"craigtest"
# }
