__author__ = 'Brian Auld'

from oslo_config import cfg
from oslo_log import log as logging
from cinder import interface
from cinder.volume import driver

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

    def create_volume(self, volume):
        
        vol_str = 'create_volume ->'        + \
            ' name: ' + volume['name']      + \
            ' id: '   + volume['id']        + \
            ' size: ' + str(volume['size']) 
        
        self.logmsg(vol_str)

    def remove_export(self, volume):

        vol_str = 'remove_export ->'        + \
            ' name: ' + volume['name']      + \
            ' id: '   + volume['id']        + \
            ' size: ' + str(volume['size'])
        log_str = 'remove_export/n'
        self.logmsg(vol_str)
        
    def create_export(self, volume):
        self.logmsg('creat_export/n')
        
    def update_volume(self, volume):
        self.logmsg('update/n')

    def delete_volume(self, volume):
        self.logmsg('delete/n')

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

    def initialize_connection(self):
        self.logmsg('init con /n')

    def terminate_connection(self):
        self.logmsg('terminate con /n')


# attachment_update        
