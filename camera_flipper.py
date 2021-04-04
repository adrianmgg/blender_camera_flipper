bl_info = {
    "name": "Camera Flipper",
    "author": "amgg",
    "version": (1, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > View > Camera Flip",
    "description": "",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}

import bpy
from mathutils import Matrix

classes_to_register = []

def register_class(cls):
    classes_to_register.append(cls)
    return cls

@register_class
class FlippedCameraData(bpy.types.PropertyGroup):
    is_flipped_camera: bpy.props.BoolProperty(default=False)
    old_use_local_camera: bpy.props.BoolProperty()
    old_local_camera: bpy.props.PointerProperty(type=bpy.types.Object)
    old_lock_rotation: bpy.props.BoolProperty()

@register_class
class ToggleCameraFlip(bpy.types.Operator):
    '''toggle camera flip'''  # TODO write a better tooltip
    bl_idname = 'view3d.flip_camera'
    bl_label = 'Toggle Camera Flip'

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'VIEW_3D' and context.space_data.region_3d.view_perspective == 'CAMERA'
    
    def execute(self, context):
        current_camera = context.space_data.camera if context.space_data.use_local_camera else context.scene.camera
        if current_camera.data.flipped_camera_data.is_flipped_camera: # is already flipped, restore original view
            context.space_data.use_local_camera = current_camera.data.flipped_camera_data.old_use_local_camera
            context.space_data.camera = current_camera.data.flipped_camera_data.old_local_camera
            context.space_data.region_3d.lock_rotation = current_camera.data.flipped_camera_data.old_lock_rotation
            bpy.data.cameras.remove(current_camera.data)
        else: # not flipped, create and switch to flipped camera
            # currently the only one supported but would like to enable creating temp. camera for viewing flipped version of viewport
            if context.space_data.region_3d.view_perspective == 'CAMERA':
                # make a copy of the current camera
                flipped_camera = current_camera.copy()
                flipped_camera.data = current_camera.data.copy()
                # TODO get the collection which this camera is in for this scene rather than adding flipped one to root of scene
                context.scene.collection.objects.link(flipped_camera)
                flipped_camera.name = f'{current_camera.name}_flipped'
                flipped_camera.matrix_world = Matrix.Identity(4) @ Matrix.Scale(-1, 4, (1, 0, 0))
                flipped_camera.hide_select = True
                flipped_camera.parent = current_camera
            # store stuff so we can restore it later
            flipped_camera.data.flipped_camera_data.is_flipped_camera = True
            flipped_camera.data.flipped_camera_data.old_local_camera = context.space_data.camera
            flipped_camera.data.flipped_camera_data.old_use_local_camera = context.space_data.use_local_camera
            flipped_camera.data.flipped_camera_data.old_lock_rotation = context.space_data.region_3d.lock_rotation
            context.space_data.use_local_camera = True
            context.space_data.camera = flipped_camera
            context.space_data.region_3d.lock_rotation = True
        return {'FINISHED'}

@register_class
class CameraFlipPanel(bpy.types.Panel):
    bl_label = 'Camera Flip'
    bl_idname = 'VIEW3D_PT_camflip'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'View'

    def draw(self, context):
        self.layout.operator('view3d.flip_camera')



def register():
    for cls in classes_to_register:
        bpy.utils.register_class(cls)
    bpy.types.Camera.flipped_camera_data = bpy.props.PointerProperty(type=FlippedCameraData)

def unregister():
    for cls in classes_to_register:
        bpy.utils.unregister_class(cls)
    del bpy.types.Camera.flipped_camera_data


if __name__ == "__main__":
    register()

