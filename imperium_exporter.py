import bpy
import math
import os

bl_info = {
    "name": "Imperium exporter",
    "description": "An add-on for rendering Imperium textures",
    "author": "Javier Rojo Muñoz",
    "version": (1, 7),
    "location": "PROPERTIES > RENDER > IMPERIUM RENDERER",
    "warning": "Further development incoming. Only works with eevee.",
    "wiki_url": "https://github.com/JavierRojo/Imperium_exporter",
    "blender": (2, 81, 0),
    "category": "Render"
}

# --- FUNCTIONS --- #
def create_shadow_catcher():
    if bpy.data.materials.find("ImpMat_shadow_catcher") == 0:
        print("returning existing material")
        return bpy.data.materials["ImpMat_shadow_catcher"]
    #else
    mat = bpy.data.materials.new(name="ImpMat_shadow_catcher") #set new material to variable
    mat.use_nodes = True
    mat.shadow_method = 'NONE'
    mat.blend_method = 'BLEND'
        
    # WORKING WITH NODES
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
        
    # create output node
    node_output = nodes.new(type='ShaderNodeOutputMaterial') 
        
    # create mix node
    mix_shader = nodes.new(type="ShaderNodeMixShader")
    mix_shader.inputs[0].default_value = 0.75
    link = links.new(mix_shader.outputs[0], node_output.inputs[0])
        
        
    # create emission node
    shadow_color = nodes.new(type="ShaderNodeEmission")
    shadow_color.inputs[0].default_value = (1,1,1,1)
    link = links.new(shadow_color.outputs[0], mix_shader.inputs[1])
        
        
    # create diffuse node
    trans = nodes.new(type="ShaderNodeBsdfTransparent")
    link = links.new(trans.outputs[0], mix_shader.inputs[2])

    # Contrast up the result
    # @TODO: force to set a single Sun lamp and give it angle 0.
    # @TODO: mark the property as a variable and test the result on a window    
    ramp = nodes.new(type="ShaderNodeMath")
    ramp.operation = 'GREATER_THAN'
    ramp.inputs[1].default_value = 0.25
    link = links.new(ramp.outputs[0], mix_shader.inputs[0])
    
    # converter RGB2BW
    rgb2bw = nodes.new(type="ShaderNodeRGBToBW")
    link = links.new(rgb2bw.outputs[0], ramp.inputs[0])
    
    # converter SHADER2RGB
    shader2rgb = nodes.new(type="ShaderNodeShaderToRGB")
    link = links.new(shader2rgb.outputs[0], rgb2bw.inputs[0])
    
    # create diffuse node
    diffuse_origin = nodes.new(type="ShaderNodeBsdfDiffuse")
    diffuse_origin.inputs[0].default_value = (1,1,1,1)
    link = links.new(diffuse_origin.outputs[0], shader2rgb.inputs[0])
    return mat

def create_holdout():
    if bpy.data.materials.find("ImpMat_holdout") == 0:
        return bpy.data.materials["ImpMat_holdout"]
    
    #else
    mat = bpy.data.materials.new(name="ImpMat_holdout") #set new material to variable
    mat.use_nodes = True
    mat.shadow_method = 'OPAQUE'
    mat.blend_method = 'BLEND'
        
    # WORKING WITH NODES
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
        
    # create output node
    node_output = nodes.new(type='ShaderNodeOutputMaterial') 
        
    # create mix node
    holdout = nodes.new(type="ShaderNodeHoldout")
    link = links.new(holdout.outputs[0], node_output.inputs[0])
    
    return mat



# --- OPERATOR CLASS --- #
class ImperiumDebug(bpy.types.Operator):
    """If you can think it, you can mess with it"""
    bl_idname = "imperium.debug"
    bl_label = "Disaster, chaos"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene
        #BEGINING OF DEBUG
        #END OF DEBUG
        return {'FINISHED'}         
        
    
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
        cam.data.clip_end = 40
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
        cam.data.clip_end = 40
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
        # @TODO: something wrong when setting 2 frames
        stepvalue = round((end-start)/n_frames)
        frames = range(start, end, stepvalue)
        if(len(frames) < 1):
            frames = [start]
        

        # Store original rotation
        original_rot = target.rotation_euler.copy()
        angle_step = math.pi*0.25
        
        count = 1
        if not os.path.exists(scene.ImperiumProperties.result_path+"color/"):
            os.mkdir(scene.ImperiumProperties.result_path+"color/")
            
            
        for f in frames:
            # Set next frame of the animation sequence
            scene.frame_set(f)
            for deg in range(8):
                # One iteration for each direction (clockwise)
                target.rotation_euler[2] = -(deg)*angle_step

                # Filepath based on frame and direction so matrix can be assembled
                scene.render.filepath = scene.ImperiumProperties.result_path + \
                    "color/"+str(deg+1) + "_"+str(count)
                try:
                    bpy.ops.render.render(write_still=True, use_viewport=False)
                except:
                    self.report({'WARNING'}, "Could not render " +
                                scene.render.filepath)
                    pass
            count += 1
        target.rotation_euler = original_rot.copy()
            
            
        # Shadow loop
        if scene.ImperiumProperties.render_shadow:
            
            bpy.ops.mesh.primitive_plane_add(enter_editmode=False, location=(0, 0, 0))
            plane = bpy.data.objects[bpy.context.active_object.name]
            plane.scale = [10,10,10]
            shadow_catcher = create_shadow_catcher()
            plane.data.materials.append(shadow_catcher) #add the material to the plane 
            plane.material_slots.update()        
            holdout = create_holdout()
            object_save_list = []
            #@TODO: deactivate all lights except Sun. Activate Sun
            for o in bpy.data.objects:
                if o.material_slots.values() == [] or o == plane:
                    continue
                else:   
                    print(o.name)             
                    save_list = []
                    for s in o.material_slots: 
                        save_list.append(s.material.name)
                        print(s.material)
                        s.material = holdout
                        print(s.material)
                    object_save_list.append([o,save_list])            
                o.material_slots.update()      

            if not os.path.exists(scene.ImperiumProperties.result_path+"shadow/"):
                os.mkdir(scene.ImperiumProperties.result_path+"shadow/")
            count = 1
            for f in frames:
                # Set next frame of the animation sequence
                scene.frame_set(f)
                for deg in range(8):
                    # One iteration for each direction (clockwise)
                    target.rotation_euler[2] = -(deg)*angle_step

                    # Filepath based on frame and direction so matrix can be assembled
                    scene.render.filepath = scene.ImperiumProperties.result_path + \
                        "shadow/"+ str(deg+1) + "_"+str(count)
                    try:
                        bpy.ops.render.render(write_still=True, use_viewport=False)
                    except:
                        self.report({'WARNING'}, "Could not render " +
                                    scene.render.filepath)
                        pass
                count += 1
            target.rotation_euler = original_rot.copy()
            #@TODO: reactivate all lights except Sun. Dectivate Sun?
            
            for e in object_save_list:
                slots = e[0].material_slots
                for s,orig_name in zip(slots,e[1]):   
                    s.material = bpy.data.materials[orig_name]           
                e[0].material_slots.update()     
            
            
            bpy.ops.object.select_all(action='DESELECT')
            plane.select_set(True)
            bpy.ops.object.delete() 
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
    
    def is_sun_light(self, object):
        return object.type == 'LIGHT' and object.data.type == 'SUN'

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
        max=256,
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
    # Decides whether to use current active camera or select one
    render_shadow: bpy.props.BoolProperty(
        name="Render shadow texture",
        description="Renders the shadow texture of current model",
        default=False
    )
    # Camera that will perform the render
    main_light: bpy.props.PointerProperty(
        name="Main light",
        description="Light that will cast the shadows",
        type=bpy.types.Object,
        poll=is_sun_light
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
        box.label(text="Output parameters")
        box.prop(scene.ImperiumProperties, "result_path", text="")
        box.prop(scene.ImperiumProperties, "render_shadow", text="Render shadow")
        if scene.ImperiumProperties.render_shadow:
            box.prop(scene.ImperiumProperties, "main_light",icon='LIGHT_SUN')

        # --- FINAL OPERATOR --- #
        row = layout.row()
        row.scale_y = 1.5
        row.operator("imperium.renderer", icon="PLAY", text="Render")
        row.operator("imperium.debug", text="DEBUG")


### --- REGISTRATION AND UNREGISTRATION OF CLASSES --- ###
def register():
    bpy.utils.register_class(ImperiumRenderer)
    bpy.utils.register_class(ImperiumCreateDefaultCamera)
    bpy.utils.register_class(ImperiumSetToDefaultCamera)
    bpy.utils.register_class(ImperiumPanel)
    bpy.utils.register_class(ImperiumDebug)

    bpy.utils.register_class(ImperiumProperties)
    bpy.types.Scene.ImperiumProperties = bpy.props.PointerProperty(
        type=ImperiumProperties)


def unregister():
    bpy.utils.unregister_class(ImperiumRenderer)
    bpy.utils.unregister_class(ImperiumCreateDefaultCamera)
    bpy.utils.unregister_class(ImperiumSetToDefaultCamera)
    bpy.utils.unregister_class(ImperiumPanel)
    bpy.utils.unregister_class(ImperiumDebug)

    bpy.utils.unregister_class(ImperiumProperties)
    del bpy.types.Scene.ImperiumProperties


if __name__ == "__main__":
    register()
