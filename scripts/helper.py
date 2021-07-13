import snappy
import spherogram

def horizontal_amalgam(tangles):
    assert len(tangles) > 0
    ans = tangles[0]
    for T in tangles[1:]:
        ans = ans | T
    return ans


def sigma(k, b, s):
    C = spherogram.RationalTangle(-s)
    Id = spherogram.IdentityBraid(1)

    tangles = k*[Id] + [C] + (2*b - k - 2)*[Id]

    return horizontal_amalgam(tangles)

