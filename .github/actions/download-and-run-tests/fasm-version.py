#!/usr/bin/env python

import fasm.version

l = []

print()
print(' FASM library version info')
print('='*75)

kl = max(len(k) for k in dir(fasm.version))
for k in dir(fasm.version):
    if '__' in k:
        continue
    v = getattr(fasm.version, k)
    if isinstance(v, str) and '\n' in v:
        l.append((k,v))
    else:
        print(" {!s}: {!r}".format(k.rjust(kl), v))

for k, v in l:
    print()
    print(k)
    print('-'*75)
    print(v)
    print('-'*75)
