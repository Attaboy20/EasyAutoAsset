bl_info = {
    "name": "EasyAutoAsset",
    "author": "Attaboy!",
    "version": (0, 1, 0),
    "blender": (3, 6, 0),
    "category": "Object",
    "location": "Outliner/3D View > Right Click Context Menu",
    "description": "Easily add the current file path to system prefs when marking assets",
}

import bpy
import os
from pathlib import Path


## TO DO ##
# UI panel for settings
# Allow user to select where to save file by picking existing libraries
# Save isolated assets button? 


class OBJECT_OT_mark_as_asset(bpy.types.Operator):
    """Mark Selected Object(s) or Collection as Asset and add file path to prefs"""
    bl_idname = "object.mark_as_asset"
    bl_label = "Mark as Asset"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        current_dir = bpy.data.filepath
        #Check if current path exists (Blend file has not been saved)
        if not current_dir:
           self.report({'WARNING'},"The current file has not been saved. Save the file first")
           return {'FINISHED'}
        selected_objects = context.selected_objects
        selected_collection = context.collection
        if selected_objects:
            for obj in selected_objects:
                obj.asset_mark()
                obj.asset_generate_preview()
                self.add_to_path()
                self.report({'INFO'}, f"Marked object as asset: {obj.name}")
        elif selected_collection:
            bpy.ops.asset.mark()
            self.add_to_path()
            self.report({'INFO'}, f"Marked collection as asset: {selected_collection.name}")
        else:
            self.report({'INFO'}, "No object or collection selected")
        return {'FINISHED'}
    
    def add_to_path(self):
        current_dir = bpy.data.filepath
       
        path_exists = False

        current_path_no_file = bpy.path.abspath("//").rstrip("\\/")
        preferences = bpy.context.preferences
        filepaths = preferences.filepaths
        asset_libraries = filepaths.asset_libraries
    
        for asset_library in asset_libraries:
            if asset_library.path == current_path_no_file:
                path_exists = True
        

        # Check if the library already exists
        # path_exists = any(asset_library.path == current_path_no_file for asset_library in asset_libraries)
        
        #existing_library = next((lib for lib in filepaths.asset_libraries if lib.name == new_library_name), None)

        if path_exists:
            self.report({'INFO'},"Path already exists in prefs.")
        else:
            new_library = bpy.ops.preferences.asset_library_add(directory=current_path_no_file, check_existing = True)
            self.report({'INFO'},f"Added new asset library: {current_path_no_file} with path: {current_dir}")

        # Save the user preferences to retain changes
        bpy.ops.wm.save_userpref()
    
    

 # For future features   
class VIEW3D_MT_mark_as_asset_submenu(bpy.types.Menu):
    bl_label = "Mark as Asset Submenu"
    bl_idname = "object.mark_as_asset_submenu"

    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_mark_as_asset.bl_idname, text="Mark as EasyAsset and add Library")

def menu_func_outliner(self, context):
    layout = self.layout
    layout.separator()
    layout.menu("object.mark_as_asset_submenu", text="Mark as EasyAsset")

def menu_func_view3d(self, context):
    layout = self.layout
    layout.separator()
    layout.menu("object.mark_as_asset_submenu", text="Mark as EasyAsset")

def menu_func_outliner_object(self, context):
    layout = self.layout
    layout.separator()
    layout.menu("object.mark_as_asset_submenu", text="Mark as EasyAsset")

def menu_func_outliner_collection(self, context):
    layout = self.layout
    layout.separator()
    layout.menu("object.mark_as_asset_submenu", text="Mark as EasyAsset")

def register():
    bpy.utils.register_class(OBJECT_OT_mark_as_asset)
    bpy.utils.register_class(VIEW3D_MT_mark_as_asset_submenu)
    bpy.types.OUTLINER_MT_context_menu.append(menu_func_outliner)
    bpy.types.OUTLINER_MT_collection.append(menu_func_outliner_collection)
    bpy.types.VIEW3D_MT_object_context_menu.append(menu_func_view3d)
    bpy.types.OUTLINER_MT_object.append(menu_func_outliner_object)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_mark_as_asset)
    bpy.utils.unregister_class(VIEW3D_MT_mark_as_asset_submenu)
    bpy.types.OUTLINER_MT_context_menu.remove(menu_func_outliner)
    bpy.types.OUTLINER_MT_collection.remove(menu_func_outliner_collection)
    bpy.types.VIEW3D_MT_object_context_menu.remove(menu_func_view3d)
    bpy.types.OUTLINER_MT_object.remove(menu_func_outliner_object)
    
    

    


if __name__ == "__main__":
    register()