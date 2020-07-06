import bpy
import math

bl_info = {
    "name": "Imperium exporter",
    "description": "An add-on for rendering Imperium textures",
    "author": "Javier Rojo Muñoz",
    "version": (1, 0),
    "location": "PROPERTIES > RENDER > IMPERIUM RENDERER",
    "warning": "Further development incoming",
    "wiki_url": "https://github.com/JavierRojo/Imperium_exporter",
    "blender": (2, 81, 0),
    "category": "Render"
}


# --- OPERATOR CLASS --- #
class ImperiumSetToDefaultCamera(bpy.types.Operator):
    """Sets any selected camera with the default settings for the Imperium renderer"""
    bl_idname = "imperium.convert_to_default_camera"
    bl_label = "Sets current camera to the Imperium default camera"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene
        if context.active_object and context.active_object.type != 'CAMERA':
            return {'CANCELLED'}

        cam = context.active_object
        # Giving a kind of isometric view to the selected camera
        cam.location = (-0.5, -4, 2.5)
        cam.rotation_euler = (math.pi*70/180, 0, 0)
        cam.data.type = 'ORTHO'
        cam.data.ortho_scale = 3
        scene.camera = cam

        # Default falue for render resolution
        bpy.context.scene.render.resolution_x = scene.ImperiumProperties.width_frame
        bpy.context.scene.render.resolution_y = scene.ImperiumProperties.width_frame
        return {'FINISHED'}


# --- IMPERIUM CREATE DEFAULT CAMERA --- #
class ImperiumCreateDefaultCamera(bpy.types.Operator):
    """Creates a default camera for the Imperium renderer"""
    bl_idname = "imperium.default_camera"
    bl_label = "Imperium default camera"
    bl_options = {'REGISTER'}

    def execute(self, context):
        # Cannot add camera in edit mode
        if context.mode != 'OBJECT':
            return {'CANCELLED'}

        scene = context.scene
        bpy.ops.object.camera_add(
            enter_editmode=False,
            align='WORLD',
            location=(-0.5, -4, 2.5),
            rotation=(math.pi*70/180, 0, 0)
        )
        # Reference to the recently created camera
        cam = bpy.data.objects[bpy.context.active_object.name]

        # Setting isometric characteristics to the camera
        cam.data.type = 'ORTHO'
        cam.data.ortho_scale = 3
        bpy.context.scene.render.resolution_x = scene.ImperiumProperties.width_frame
        bpy.context.scene.render.resolution_y = scene.ImperiumProperties.width_frame

        # Sets current camera as the main camera
        scene.camera = cam
        return {'FINISHED'}


# --- IMPERIUM RENDERER --- #
class ImperiumRenderer(bpy.types.Operator):
    """Render the Imperium textures into an output folder"""
    bl_idname = "imperium.renderer"
    bl_label = "Imperium texture render"
    bl_options = {'REGISTER'}

    def execute(self, context):
        # Declaring useful variables
        scene = context.scene
        n_frames = scene.ImperiumProperties.number_of_frames
        start = scene.frame_start
        end = scene.frame_end
        target = scene.ImperiumProperties.main_target

        # Checking that there is a target
        bpy.ops.object.select_all(action='DESELECT')
        if(not target):
            self.report({'WARNING'}, "Target must be set")
            return{'CANCELLED'}

        # Checking if camera is available
        if scene.ImperiumProperties.use_active_camera:
            cam = scene.camera
        else:
            cam = scene.ImperiumProperties.main_camera
        if (not cam):
            self.report({'WARNING'}, "Camera must be set")
            return{'CANCELLED'}

        # Always render transparent background
        scene.render.film_transparent = True

        # Divide the timeline into even sections
        stepvalue = round((end-start)/n_frames)
        frames = range(start, end, stepvalue)
        if(len(frames) < 1):
            frames = [start]
        count = 1

        # Store original rotation
        original_rot = target.rotation_euler.copy()
        angle_step = math.pi*0.25

        for f in frames:
            # Set next frame of the animation sequence
            scene.frame_set(f)
            for deg in range(8):
                # One iteration for each direction (clockwise)
                target.rotation_euler[2] = -(deg)*angle_step

                # Filepath based on frame and direction so matrix can be assembled
                scene.render.filepath = scene.ImperiumProperties.result_path + \
                    str(deg+1) + "_"+str(count)
                try:
                    bpy.ops.render.render(write_still=True, use_viewport=False)
                except:
                    self.report({'WARNING'}, "Could not render " +
                                scene.render.filepath)
                    pass
            count += 1
        target.rotation_euler = original_rot.copy()
        return {'FINISHED'}


# --- VARIABLES CLASS --- #
class ImperiumProperties(bpy.types.PropertyGroup):
    """Properties for the imperium renderer addon"""

    # Filter funciton for poll callback when selecting target
    def is_valid_target(self, object):
        if (self.mesh_as_target):
            return object.type == 'MESH'
        else:
            return object.type == 'EMPTY'

    def is_camera(self, object):
        return object.type == 'CAMERA'

    # Coordinates the resolution set for x and y axis
    def define_width(self, context):
        bpy.context.scene.render.resolution_x = self.width_frame
        bpy.context.scene.render.resolution_y = self.width_frame
        return None

    # Number of steps that we want to render
    number_of_frames: bpy.props.IntProperty(
        name="Frame to render",
        default=1,
        min=1,
        max=50
    )
    # Width, in pixels, of each tile
    width_frame: bpy.props.IntProperty(
        name="Width of frames",
        default=64,
        min=1,
        max=128,
        update=define_width,
        subtype='PIXEL'
    )
    # Output folder to store the tiles
    result_path: bpy.props.StringProperty(
        name="Output Path",
        default=".",
        description="Define the path where to export to",
        subtype='DIR_PATH'
    )
    # Object that will be used as render target
    main_target: bpy.props.PointerProperty(
        name="Main target",
        description="Main empty target for the imperium rendering workflow",
        type=bpy.types.Object,
        poll=is_valid_target
    )
    # Decides if target is a mesh or an empty
    mesh_as_target: bpy.props.BoolProperty(
        name="Use mesh as target",
        description="Use a mesh instead of an empty as a target",
        default=False
    )
    # Camera that will perform the render
    main_camera: bpy.props.PointerProperty(
        name="Main camera",
        description="Main camera to perform the rendering",
        type=bpy.types.Object,
        poll=is_camera
    )
    # Decides whether to use current active camera or select one
    use_active_camera: bpy.props.BoolProperty(
        name="Use active camera",
        description="Use the active camera if posible",
        default=True
    )


# --- UI IMPERIUM PANEL --- #
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
        layout.label(text="Version: 1.0.0", icon='SCRIPT')

        # --- FRAME PROPERTIES --- #
        box = layout.box()
        box.label(text="Frame information")
        col = box.column(align=True)
        col.prop(scene, "frame_start", text="start")
        col.prop(scene, "frame_end", text="end")
        col.prop(scene.ImperiumProperties,
                 "number_of_frames", text="number of frames")
        row = box.row()
        row.prop(scene.ImperiumProperties, "width_frame", text="width")

        # --- TARGET --- #
        layout.row()
        box = layout.box()
        box.label(text="Target")
        row = box.row()
        box.prop(scene.ImperiumProperties,
                 "mesh_as_target", text="look for meshes")
        # A different icon is used depending on the target nature
        if scene.ImperiumProperties.mesh_as_target:
            box.prop(scene.ImperiumProperties, "main_target",
                     text="", icon='MESH_CUBE')
        else:
            box.prop(scene.ImperiumProperties,
                     "main_target", text="", icon='TRACKER')

        # --- CAMERA --- #
        row = layout.row()
        box = layout.box()
        box.label(text="Camera")

        # If not in object mode, no new cameras can be added
        if context.mode == 'OBJECT':
            # If a camera is selected, propose its modification instead of creating a new one
            if context.active_object and context.active_object.type == 'CAMERA':
                box.operator("imperium.convert_to_default_camera",
                             icon="OUTLINER_DATA_CAMERA", text="Convert to default camera")
            else:
                box.operator("imperium.default_camera",
                             icon="OUTLINER_DATA_CAMERA", text="Generate default camera")

        row = box.row()
        row.prop(scene.ImperiumProperties,
                 "use_active_camera", text="use active camera")
        # If no active camera allows the user to select one
        if not scene.ImperiumProperties.use_active_camera:
            row.prop(scene.ImperiumProperties, "main_camera",
                     text="camera", icon='OUTLINER_DATA_CAMERA')

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
