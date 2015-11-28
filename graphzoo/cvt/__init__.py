__all__ = ['fields', 'CVTGraph', 'info']

from sage.graphs.graph import Graph
from sage.rings.integer import Integer
from ..query import Table
from ..utility import isinteger
from ..utility import lookup
from ..zoograph import ZooGraph
from ..zoograph import canonical_label
from ..zooobject import ZooInfo

_objspec = {
    "name": "graph_cvt",
    "dict": "_cvtprops",
    "primary_key": "id",
    "indices": {"cvt_index"},
    "skip": {"id"},
    "fields" : {
        "cvt_index": Integer,
        "id": (ZooGraph, {"primary_key"})
    },
    "compute": {},
    "default": {
        "_props": {
            "average_degree": 3,
            "is_regular": True,
            "is_tree": False,
            "is_vertex_transitive": True
        }
    }
}

class CVTGraph(ZooGraph):
    _cvtprops = None
    _spec = _objspec
    _parent = ZooGraph

    def __init__(self, data = None, index = None, **kargs):
        cl = CVTGraph
        self._init_(cl, kargs, defNone = ["order"],
                    setVal = {"data": data, "index": index},
                    setProp = {"cvt_index": "index"})

        if kargs["order"] is not None and kargs["index"] is not None:
            join = Table(cl._spec["name"]).join(Table(cl._parent._spec["name"]),
                         by = {cl._spec["primary_key"]})
            r = self._db_read(cl._parent, join, {"order": kargs["order"],
                                                 "cvt_index": kargs["index"]})
            kargs["zooid"] = r["id"]
            kargs["graph"] = None
        ZooGraph.__init__(self, **kargs)

        if kargs["order"] is not None:
            assert(kargs["order"] == self._props["order"])
        if self._cvtprops is None:
            self._db_read(cl)
        if kargs["cur"] is not None:
            self._db_write(cl, kargs["cur"])

    def _parse_params(self, d):
        if isinteger(d["data"]):
            if d["index"] is None:
                d["zooid"] = Integer(d["data"])
            else:
                d["order"] = Integer(d["data"])
            d["data"] = None
            return True
        else:
            return False

    def _clear_params(self, d):
        d["order"] = None
        d["index"] = None

    def _repr_(self):
        name = "Cubic vertex-transitive graph on %d vertices, number %d" \
                                            % (self.order(), self.cvt_index())
        if self.name() != '':
            name = self.name() + ": " + name
        return name

    def cvt_index(self):
        return lookup(self._cvtprops, "cvt_index")

info = ZooInfo(CVTGraph)

def import_cvt(file, db = None, format = "sparse6", verbose = False):
    if db is None:
        db = info.getdb()
    info.initdb(db = db, commit = False)
    previous = 0
    i = 0
    cur = db.cursor()
    with open(file) as f:
        for line in f:
            data = line.strip()
            if format not in ["graph6", "sparse6"]:
                data = eval(data)
            g = Graph(data)
            n = g.order()
            if n > previous:
                if verbose and n > 0:
                    print "Imported %d graphs of order %d" % (i, previous)
                previous = n
                i = 0
            i += 1
            CVTGraph(graph = g, order = n, index = i, cur = cur, db = db)
        if verbose:
            print "Imported %d graphs of order %d" % (i, n)
        f.close()
    cur.close()
    db.commit()
