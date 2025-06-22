import importlib

modules = [
    'runepy.ui.editor.controller',
    'runepy.ui.editor.gizmos',
    'runepy.ui.editor.serializer',
]

for mod in modules:
    importlib.import_module(mod)
