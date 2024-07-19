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
from bpy.types import Panel, Context, Menu
from bpy.props import StringProperty


class PoseLibraryPanel:
    @classmethod
    def pose_library_panel_poll(cls, context: Context) -> bool:
        return bool(context.object and context.object.mode == 'POSE')

    @classmethod
    def poll(cls, context: Context) -> bool:
        return cls.pose_library_panel_poll(context)


## TO DO ##
# UI panel for settings
# Allow user to select where to save file by picking existing libraries
# Save isolated assets button? 
# Poses?


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
    
    @staticmethod
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

class POSE_OT_mark_pose(bpy.types.Operator):
    """Mark Selected Bone(s) as Pose Asset and add file path to prefs"""
    bl_label = "Enter name for Pose Asset"
    bl_idname = "pose.mark_pose"
    bl_options = {'REGISTER', 'UNDO'}
    
    easy_pose_name: StringProperty(
        name="Pose Name",
        description="Name of the pose asset",
        default="EasyPose"
    )

    @classmethod
    def poll(cls, context):
        # Ensure an object is selected and in pose mode
        obj = context.active_object
        return obj is not None and obj.mode == 'POSE'
    
    def invoke(self, context, event):
        # Open a dialog for the user to enter the pose name
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        current_dir = bpy.data.filepath
        # Check if current path exists (Blend file has not been saved)
        if not current_dir:
            self.report({'WARNING'}, "The current file has not been saved. Save the file first")
            return {'FINISHED'}
        obj = context.active_object
        bpy.ops.poselib.create_pose_asset(pose_name=self.easy_pose_name, activate_new_action=True)
        obj.asset_generate_preview()
        OBJECT_OT_mark_as_asset.add_to_path(self)
        self.report({'INFO'}, f"Pose '{self.easy_pose_name}' marked as pose asset")
        return {'FINISHED'}


#Adds Panel to Animation Editors
class POSE_MT_mark_pose_panel(Panel):
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "UI"
    bl_label = "Create EasyPose"
    bl_category = "Action"

    @classmethod
    def poll(cls, context):
        # Ensure an object is selected and in pose mode
        obj = context.active_object
        return obj is not None and obj.mode == 'POSE'
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("POSE_OT_mark_pose", text="Mark EasyPose Asset")
        # Add button to return to previous action when making a new one
        if bpy.types.POSELIB_OT_restore_previous_action.poll(context):
            row.operator("poselib.restore_previous_action", text="", icon='LOOP_BACK')
        #row.operator("poselib.create_pose_asset").activate_new_action = True

 # For future features   
class VIEW3D_MT_mark_as_asset_submenu(bpy.types.Menu):
    bl_label = "Mark as Asset Submenu"
    bl_idname = "object.mark_as_asset_submenu"

    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_mark_as_asset.bl_idname, text="Mark as EasyAsset and add Library")
        layout.operator(POSE_OT_mark_pose.bl_idname, text="Mark EasyPose and add Library")
        

def menu_func_outliner(self, context):
    layout = self.layout
    layout.separator()
    layout.menu("object.mark_as_asset_submenu", text="Mark as EasyAsset")

def menu_func_view3d(self, context):
    layout = self.layout
    layout.separator()
    layout.menu("object.mark_as_asset_submenu", text="Mark as EasyAsset")
    
def menu_func_pose(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(POSE_OT_mark_pose.bl_idname, text="Mark Pose as EasyPose Asset")

def menu_func_outliner_object(self, context):
    layout = self.layout
    layout.separator()
    layout.menu("object.mark_as_asset_submenu", text="Mark as EasyAsset")

def menu_func_outliner_collection(self, context):
    layout = self.layout
    layout.separator()
    layout.menu("object.mark_as_asset_submenu", text="Mark as EasyAsset")
    
classes = (
    OBJECT_OT_mark_as_asset,
    POSE_OT_mark_pose,
    POSE_MT_mark_pose_panel,
    VIEW3D_MT_mark_as_asset_submenu,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_pose_context_menu.append(menu_func_pose)
    bpy.types.DOPESHEET_PT_asset_panel.append(POSE_OT_mark_pose)
    bpy.types.DOPESHEET_PT_asset_panel.append(POSE_MT_mark_pose_panel)
    bpy.types.OUTLINER_MT_context_menu.append(menu_func_outliner)
    bpy.types.OUTLINER_MT_collection.append(menu_func_outliner_collection)
    bpy.types.VIEW3D_MT_object_context_menu.append(menu_func_view3d)
    bpy.types.OUTLINER_MT_object.append(menu_func_outliner_object)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_pose_context_menu.remove(menu_func_pose)
    bpy.types.DOPESHEET_PT_asset_panel.remove(POSE_OT_mark_pose)
    bpy.types.DOPESHEET_PT_asset_panel.remove(POSE_MT_mark_pose_panel)
    bpy.types.OUTLINER_MT_context_menu.remove(menu_func_outliner)
    bpy.types.OUTLINER_MT_collection.remove(menu_func_outliner_collection)
    bpy.types.VIEW3D_MT_object_context_menu.remove(menu_func_view3d)
    bpy.types.OUTLINER_MT_object.remove(menu_func_outliner_object)
    
    


if __name__ == "__main__":
    register()