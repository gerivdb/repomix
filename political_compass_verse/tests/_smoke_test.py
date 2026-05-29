import sys
sys.path.insert(0, r"D:\DO\WEB\TOOLS\L4-TOOLS\VERSUS")

from political_compass_verse import (
    PoliticalCompassVerse,
    TritPoliticalEncode,
    TritQuadruplet,
    TritPoliticalDistance,
    TritPoliticalProject,
    TritPoliticalMerge,
    TritPoliticalRender,
)

v = PoliticalCompassVerse()
print("diamond:", v.diamond_position)

q = v.encode("capitalisme_surveillance")
print("surveillance:", q)

d = v.distance_from_diamond("libertarien")
print("distance libertarien:", d)

d2 = v.distance_from_diamond("communisme_plateforme")
print("distance communisme_plateforme:", d2)

report = v.distance_from_diamond("diamond")
print("distance diamond:", report)

m = v.merge(TritQuadruplet(2,0,2,1), TritQuadruplet(0,2,0,2))
print("merge diamond+surveillance:", m)

mermaid = v.render_mermaid()
print("mermaid length:", len(mermaid))

print("ALL OK")
