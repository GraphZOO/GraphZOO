import re
from types import MethodType
from ..query import Table
from ..utility import default
from ..utility import isinteger
from ..utility import lookup
from ..zooentity import ZooEntity
from ..zooentity import ZooInfo

class ZooObject(ZooEntity):
    _zooprops = None
    _spec = None
    _zooid = None
    _unique_id = None
    _parent = ZooEntity
    _dict = "_zooprops"
    _extra_props = None
    _fields = None

    def __init__(self, data = None, **kargs):
        self._init_(ZooObject, kargs, setVal = {"data": data})

    def _init_defaults(self, d):
        default(d, "zooid")
        default(d, "unique_id")

    def _parse_params(self, d):
        if isinteger(d["data"]):
            d["zooid"] = Integer(d["data"])
            d["data"] = None
            return True
        elif isinstance(d["data"], basestring) \
                and re.match(r'^[0-9A-Fa-f]{64}$', d["data"]):
            d["unique_id"] = Integer(d["data"])
            d["data"] = None
        else:
            return False

    def _init_object(self, cl, d, setProp = {}):
        if self._zooid is None:
            self._zooid = d["zooid"]
        if self._unique_id is None:
            self._unique_id = d["unique_id"]
        if self._zooid is None or self._unique_id is None:
            if d["cur"] is None:
                r = self._db_read(cl)
                self._zooid = r["zooid"]
                self._unique_id = r["unique_id"]
        ZooEntity.__init__(self, **d)

    def _copy_props(self, cl, obj):
        c = cl
        while c is not None:
            if isinstance(obj, c):
                self._setprops(c, obj._getprops(c))
            c = c._parent
        c = obj.__class__
        cl = self.__class__
        while c is not None and not issubclass(cl, c):
            self.__setattr__(c._dict, obj._getprops(c))
            self._extra_props.add(c._dict)
            c = c._parent
        for p in obj._extra_props:
            try:
                self.__getattribute__(p)
            except AttributeError:
                self.__setattr__(p, obj.__getattribute__(p))
                self._extra_props.add(p)
        for a in dir(obj):
            if a not in dir(self):
                attr = obj.__getattribute__(a)
                if isinstance(attr, MethodType):
                    self.__setattr__(a, MethodType(attr.im_func, self, cl))

    def _db_read_nonprimary(self, cur = None):
        if self._unique_id is not None:
            query = {"unique_id": self._unique_id}
            cur = self._db.query([ZooObject._spec["primary_key"]],
                                 Table(ZooObject._spec["name"]),
                                 query, cur = cur)
            r = cur.fetchone()
            if r is None:
                raise KeyError(query)
            self._zooid = r[0]
            return True
        return False

    def alias(self):
        try:
            return lookup(self._zooprops, "alias")
        except KeyError:
            self._zooprops["alias"] = ZooObject._spec["fields"]["alias"](self._zooid)
            return self._zooprops["alias"]

    def unique_id(self):
        if self._unique_id is None:
            raise NotImplementedError
        return self._unique_id

info = ZooInfo(ZooObject)
