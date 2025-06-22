import runepy.debug as dbg

d = dbg.get_debug()
assert hasattr(d, 'attach')
# If Panda3D absent the call should NO-OP without error

d.attach(None)
