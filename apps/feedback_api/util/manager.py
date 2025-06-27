from util.base.manager_base import DBManagerBase
from util.manager_mixins import InitMixin, DropMixin, QueryMixin 

class DBManager(DBManagerBase, InitMixin, DropMixin, QueryMixin):
    pass
