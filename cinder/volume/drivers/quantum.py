__author__ = 'Brian Auld'

from oslo_config import cfg
from oslo_log import log as logging
from cinder import interface
from cinder.volume import driver
import requests

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

        # # this should be GET'ed
        # r = request.get('https://10.134.204.84:8080/p3api/v2/api/vPG?vpgName=VG509')
        # print(r)

    def raise_assert(str):
        assert False,str

    def logmsg(self, string):
        LOG.info('qmco_api ' + string)

    def do_setup(self, context):
        
        self.logmsg('do setup /n')

# volume show testvol
# +--------------------------------+-------------------------------------------+
# | Field                          | Value                                     |
# +--------------------------------+-------------------------------------------+
# | attachments                    | []                                        |
# | availability_zone              | nova                                      |
# | bootable                       | false                                     |
# | consistencygroup_id            | None                                      |
# | created_at                     | 2022-03-12T00:20:56.000000                |
# | description                    | None                                      |
# | encrypted                      | False                                     |
# | id                             | 8fc7c1e9-a84b-4c3b-8311-b4566fcf1d4b      |
# | migration_status               | None                                      |
# | multiattach                    | False                                     |
# | name                           | testvol                                   |
# | os-vol-host-attr:host          | den-bauld-dstack-barbican@quantum#quantum |
# | os-vol-mig-status-attr:migstat | None                                      |
# | os-vol-mig-status-attr:name_id | None                                      |
# | os-vol-tenant-attr:tenant_id   | 140c34550b6540bdb5ff001c91be16ef          |
# | properties                     |                                           |
# | replication_status             | None                                      |
# | size                           | 10                                        |
# | snapshot_id                    | None                                      |
# | source_volid                   | None                                      |
# | status                         | available                                 |
# | type                           | quantum                                   |
# | updated_at                     | 2022-03-12T00:21:14.000000                |
# | user_id                        | 73b407f49ae04b489889977d669e28a9          |
# +--------------------------------+-------------------------------------------+

    def remove_export(self, context, volume):

        vol_str = 'remove_export ->'        + \
            ' name: ' + volume['name']      + \
            ' id: '   + volume['id']        + \
            ' size: ' + str(volume['size'])
        self.logmsg(vol_str)

# Volume(
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
        
    def create_volume(self, volume):
        
        vol_str = 'create_volume start ->'        + \
            ' name: ' + volume['display_name']      + \
            ' id: '   + volume['id']        + \
            ' size: ' + str(volume['size']) 
        self.logmsg(vol_str)

        # 1. get vpgid
        # =====================================================================================
        url_base = 'https://10.134.204.84:8080/p3api/v2/api/'
        vpg = "VG509"
        params = {"vpgName":vpg, "async": "false"}
        data   = {}
        r = requests.get(url_base + "vPG", params=params, data=data, auth=('pivot3','pivot3'), verify=False)
        self.logmsg( 'get return status_code:{}'.format(r.status_code))
        if ( r.status_code == 200 ):
            r_json = r.json()
            vpgid =  r_json[0]['vpgid']
        else:
            raise_assert("vpgid was not retrievable")

    
        # 2. use vpgid to create volume
        # =====================================================================================
        self.logmsg('create_volume proceed - vpgId:{}'.format(vpgid))
        params = {"vpgId" : vpgid, "async" : "false"}
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
                "initiatorName": "IscsiInitiatorName",
                "access": "readwrite"
            }
        }
        r = requests.post(url_base + "vPG/vsVolume", params=params, json=data, auth=('pivot3','pivot3'), verify=False)
        self.logmsg( 'post return status_code:{}'.format(r.status_code))
        if ( r.status_code == 201 and len(r.content)):
            self.logmsg('create_volume done')
            return
        else:
            raise_assert('Got status code:{} with response:{}'.format(r.status_code, r.text))

            self.logmsg('create_volume done error')

    def delete_volume(self, volume):
        vol_str = 'delete_volume start ->'        + \
            ' name: ' + volume['display_name']      + \
            ' id: '   + volume['id']        + \
            ' size: ' + str(volume['size']) 
        self.logmsg(vol_str)

        # 1. get vpgid
        # =====================================================================================
        url_base = 'https://10.134.204.84:8080/p3api/v2/api/'
        vpg = "VG509"
        params = {"vpgName":vpg, "async": "false"}
        data   = {}
        r = requests.get(url_base + "vPG", params=params, data=data, auth=('pivot3','pivot3'), verify=False)
        self.logmsg( 'get return status_code:{}'.format(r.status_code))
        if ( r.status_code == 200 ):
            r_json = r.json()
            vpgid =  r_json[0]['vpgid']
        else:
            raise_assert("vpgid was not retrievable")

    
        # 2. use vpgid to delete volume
        # =====================================================================================
        self.logmsg('delete proceed - vpgId:{}'.format(vpgid))
        params = {"vpgId" : vpgid, "async" : "false", "volumeName" : volume['display_name']}
        data   = {}
        r = requests.delete(url_base + "vPG/vsVolume", params=params, json=data, auth=('pivot3','pivot3'), verify=False)
        self.logmsg( 'post return status_code:{}'.format(r.status_code))
        if ( r.status_code == 200 ):
            self.logmsg('delete_volume done')
            return
        else:
            raise_assert('Got status code:{} with response:{}'.format(r.status_code, r.text))

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

    def attach_volume(self):
        self.logmsg('attach/n')

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

# conn_info return to caller     
{'driver_volume_type': 'iscsi',
 'data': {'target_discovered': False,
          'target_portal': '10.134.204.85:3260',
          'target_iqn': 'iqn.2010-10.org.openstack:volume-348e5c49-41f2-4896-83f0-853588889fd5',
          'target_lun': 0,
          'volume_id': '348e5c49-41f2-4896-83f0-853588889fd5',
          'auth_method': 'CHAP',
          'auth_username': 'cAeghKukHVNeC7eJzp2b',
          'auth_password': '8kU8FoRQWXJYE7ku',
          'encrypted': False}}
     
    def initialize_connection(self):
        self.logmsg('init con /n')

    def terminate_connection(self):
        self.logmsg('terminate con /n')


# attachment_update        
