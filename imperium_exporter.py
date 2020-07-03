import bpy
import math

bl_info = {
    "name": "Imperium exporter",
    "description": "An add-on for rendering Imperium textures",
    "author": "Javier Rojo Muñoz",
    "version": (0, 7),
    "location": "PROPERTIES > RENDER > IMPERIUM RENDERER",
    "warning": "Under development: T1-04",
    "wiki_url": "https://github.com/JavierRojo/Imperium_exporter",
    "blender": (2, 81, 0),
    "category": "Render"
}


### --- OPERATOR CLASS --- ###
class ImperiumSetToDefaultCamera(bpy.types.Operator):
    """Sets any selected camera to a default for the Imperium renderer"""
    bl_idname = "imperium.convert_to_default_camera"
    bl_label = "Sets current camera to the Imperium default camera"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        scene = context.scene
        if context.active_object and context.active_object.type != 'CAMERA':
            return {'CANCELLED'}
        
        
        cam = context.active_object
        cam.location=(-1, -4, 3)
        cam.rotation_euler=(math.pi*2.5/6, 0, 0)
        print(cam.data.name)
        cam.data.type = 'ORTHO'
        scene.camera = cam
        
        #angle = math.atan(1/(math.sqrt(2))) # 0.615 rad ~= 35.264º
        #bpy.ops.object.camera_add(
        #    enter_editmode=False,
        #    align='WORLD',
        #    location=(-1, -4, 3),
        #    rotation=(math.pi*2.5/6, 0, 0)
        #)
        #theory for isometric angle:
        #cam = bpy.data.objects[bpy.context.active_object.name]
        #cam.data.type = 'ORTHO'
        #scene.camera = cam
        # @TODO: Add a guide cube of empties to place the character in
        return {'FINISHED'}
    
class ImperiumCreateDefaultCamera(bpy.types.Operator):
    """Creates a default camera for the Imperium renderer"""
    bl_idname = "imperium.default_camera"
    bl_label = "Imperium default camera"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        scene = context.scene
        #angle = math.atan(1/(math.sqrt(2))) # 0.615 rad ~= 35.264º
        bpy.ops.object.camera_add(
            enter_editmode=False,
            align='WORLD',
            location=(-1, -4, 3),
            rotation=(math.pi*2.5/6, 0, 0)
        )
        #theory for isometric angle:
        cam = bpy.data.objects[bpy.context.active_object.name]
        cam.data.type = 'ORTHO'
        scene.camera = cam
        # @TODO: Add a guide cube of empties to place the character in
        return {'FINISHED'}


class ImperiumRenderer(bpy.types.Operator):
    """Render the Imperium textures"""
    bl_idname = "imperium.renderer"
    bl_label = "Imperium texture render"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        scene = context.scene
        n_frames = scene.ImperiumProperties.number_of_frames
        start = scene.frame_start
        end = scene.frame_end
        target = scene.ImperiumProperties.main_target
        bpy.ops.object.select_all(action='DESELECT')
        if(not target):
            self.report({'WARNING'}, "Target must be set")
            return{'CANCELLED'}       
        
        
        if scene.ImperiumProperties.use_active_camera:
            cam = scene.camera
        else:
            cam = scene.ImperiumProperties.main_camera
        
        if (not cam):
            self.report({'WARNING'}, "Camera must be set")
            return{'CANCELLED'}
            

        stepvalue = round((end-start)/n_frames)
        frames = range(start, end, stepvalue)
        if(len(frames) < 1):
            frames = [start]
        count = 1
        original_rot = target.rotation_euler.copy()
        angle_step = math.pi*0.25
        bpy.context.scene.render.film_transparent = True

        for f in frames:
            scene.frame_set(f)
            for deg in range(8):
                target.rotation_euler[2] = -(deg)*angle_step
                scene.render.filepath = scene.ImperiumProperties.result_path + \
                    str(deg+1) + "_"+str(count)
                try:
                    bpy.ops.render.render(write_still=True, use_viewport=False)
                except:
                    self.report({'WARNING'}, "Could not render "+scene.render.filepath)
                    pass
            target.rotation_euler = original_rot.copy()
            count += 1
            
        return {'FINISHED'}


### --- VARIABLES CLASS --- ###


class ImperiumProperties(bpy.types.PropertyGroup):
    """Properties for this addon"""
    
    def is_valid_target(self, object):
        if (self.mesh_as_target):
            return object.type == 'MESH'
        else:
            return object.type == 'EMPTY'
    def is_camera(self, object):
        return object.type == 'CAMERA'
    
    def define_width(self,context):
        bpy.context.scene.render.resolution_x = self
        bpy.context.scene.render.resolution_y = self
        return None
    
    number_of_frames: bpy.props.IntProperty(
        name="Frame to render",
        default=1,
        min=1,
        max=50
    )
    width_frame: bpy.props.IntProperty(
        name="Width of frames",
        default=64,
        min=1,
        max=128,
        update = define_width,
        subtype = 'PIXEL'
    )
    result_path: bpy.props.StringProperty(
        name="Output Path",
        default=".",
        description="Define the path where to export to",
        subtype='DIR_PATH'
    ) 
    main_target: bpy.props.PointerProperty(
        name="Main target",
        description="Main empty target for the imperium rendering workflow",
        type=bpy.types.Object,
        poll= is_valid_target
    )    
    mesh_as_target: bpy.props.BoolProperty(
        name="Use mesh as target",
        description="Use a mesh instead of an empty as a target",
        default=False
    )    
    main_camera: bpy.props.PointerProperty(
        name="Main camera",
        description="Main camera to perform the rendering",
        type=bpy.types.Object,
        poll=is_camera
    )
    use_active_camera: bpy.props.BoolProperty(
        name="Use active camera",
        description="Use the active camera if posible",
        default=True
    )  
    
    

### --- UI CLASS --- ###


class ImperiumPanel(bpy.types.Panel):
    """Main panel for the add-on"""
    bl_idname = "OBJECT_PT_hello_world"
    bl_label = "Imperium renderer"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        ### --- SECOND ITERATION --- ###
        layout.label(text="T1-06", icon='SCRIPT')

        # --- FRAME PROPERTIES --- #
        box = layout.box()
        box.label(text="Frame information")
        col = box.column(align=True)
        col.prop(scene, "frame_start", text="start")
        col.prop(scene, "frame_end", text="end")
        col.prop(scene.ImperiumProperties,
                 "number_of_frames", text="number of frames")
        row = box.row()
        row.prop(scene.ImperiumProperties,"width_frame", text="width")        
                
        # --- TARGET --- #
        layout.row()
        box = layout.box()
        box.label(text="Target")
        row = box.row()        
        box.prop(scene.ImperiumProperties, "mesh_as_target", text="look for meshes")
        if scene.ImperiumProperties.mesh_as_target:
            box.prop(scene.ImperiumProperties, "main_target", text="", icon='MESH_CUBE')
        else:
            box.prop(scene.ImperiumProperties, "main_target", text="", icon='TRACKER')
        
        # --- CAMERA --- #
        row =layout.row()
        box = layout.box()
        box.label(text="Camera")
        
        if context.active_object and context.active_object.type == 'CAMERA':
            box.operator("imperium.convert_to_default_camera", icon="OUTLINER_DATA_CAMERA", text="Convert to default camera")
        else:
            box.operator("imperium.default_camera", icon="OUTLINER_DATA_CAMERA", text="Generate default camera")
        
        row = box.row()
        row.prop(scene.ImperiumProperties, "use_active_camera", text="use active camera")
        if not scene.ImperiumProperties.use_active_camera:
            row.prop(scene.ImperiumProperties, "main_camera", text="camera", icon='OUTLINER_DATA_CAMERA')
        
        # --- PATH --- #
        box = layout.box()
        box.label(text="Output path")
        box.prop(scene.ImperiumProperties, "result_path", text="")

        # --- FINAL OPERATOR --- #
        row = layout.row()
        row.scale_y = 1.5
        row.operator("imperium.renderer", icon="PLAY", text="Render")


### --- REGISTRATION AND UNREGISTRATION OF CLASSES --- ###
def register():
    bpy.utils.register_class(ImperiumRenderer)
    bpy.utils.register_class(ImperiumCreateDefaultCamera)
    bpy.utils.register_class(ImperiumSetToDefaultCamera)
    bpy.utils.register_class(ImperiumPanel)

    bpy.utils.register_class(ImperiumProperties)
    bpy.types.Scene.ImperiumProperties = bpy.props.PointerProperty(
        type=ImperiumProperties)
        
def unregister():
    bpy.utils.unregister_class(ImperiumRenderer)
    bpy.utils.unregister_class(ImperiumCreateDefaultCamera)
    bpy.utils.unregister_class(ImperiumSetToDefaultCamera)
    bpy.utils.unregister_class(ImperiumPanel)

    bpy.utils.unregister_class(ImperiumProperties)
    del bpy.types.Scene.ImperiumProperties


if __name__ == "__main__":
    register()