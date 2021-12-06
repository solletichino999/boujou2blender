# Add-on metadata
bl_info = {
    "name": "Boujou 2 Blender",
    "author": "Simone Spadino",
    "description": "Imports the tracking data from Boujou txt file.",
    "version": (1, 0, 0),
    "blender": (2, 93, 0),
    "location": "File > Import > Boujou",
    "url": "https://github.com/solletichino999/boujou2blender",
    "doc_url": "https://github.com/solletichino999/boujou2blender",
    "tracker_url": "https://github.com/solletichino999/boujou2blender/issues",
    "category": "Import-Export"
}

# Wrap the blender related code in a try-catch block to silently fail if
# import bpy fails. This is to allow the unit testing code to import boujou2blender.py
try:
    # TODO: make reloading work
    if "bpy" in locals():
        import importlib
        importlib.reload(boujou2blender)
    else:
        from . import boujou2blender

    import bpy

    # Only needed if you want to add into a dynamic menu
    def menu_func_import(self, context):
        self.layout.operator(boujou2blender.SlideshowAddSlide.bl_idname, text="Boujou (.txt)")

    def register():
        bpy.utils.register_class(boujou2blender.SlideshowAddSlide)
        # Add import menu item
        if hasattr(bpy.types, 'TOPBAR_MT_file_import'):
            #2.8+
            bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
        #else:
            #bpy.types.INFO_MT_file_import.append(menu_func_import)

    def unregister():
        bpy.utils.unregister_class(boujou2blender.SlideshowAddSlide)
        # Remove import menu item
        if hasattr(bpy.types, 'TOPBAR_MT_file_import'):
            #2.8+
            bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
        #else:
            #bpy.types.INFO_MT_file_import.remove(menu_func_import)


    if __name__ == "__main__":
        register()

except ImportError:
    # assume no bpy module. fail silently
    pass
