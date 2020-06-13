import bpy

bl_info = {
    "name": "Imperium exporter",
    "description": "An add-on for rendering Imperium textures",
    "author": "Javier Rojo Muñoz",
    "version": (0, 2),
    "location": "PROPERTIES > RENDER > IMPERIUM RENDERER",
    "warning": "Under development",
    "wiki_url": "https://github.com/JavierRojo/Imperium_exporter",
    "blender": (2, 81, 0),
    "category": "Render"
}


### --- OPERATOR CLASS --- ###


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

        stepvalue = round((end-start)/n_frames)
        frames = range(start, end, stepvalue)
        if(len(frames) < 1):
            frames = [start]
        count = 0
        for f in frames:
            scene.frame_set(f)
            scene.render.filepath = scene.ImperiumProperties.result_path + \
                str(count)
            bpy.ops.render.render(write_still=True, use_viewport=False)
            count += 1
        return {'FINISHED'}


### --- VARIABLES CLASS --- ###


class ImperiumProperties(bpy.types.PropertyGroup):
    """Properties for this addon"""
    number_of_frames: bpy.props.IntProperty(
        name="Frame to render",
        default=1,
        min=1,
        max=50
    )
    result_path: bpy.props.StringProperty(
        name="Output Path",
        default=".",
        description="Define the path where to export to",
        subtype='DIR_PATH'
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
        layout.label(text="T1-02", icon='SCRIPT')

        # --- FRAME PROPERTIES --- #
        row = layout.row()
        col = layout.column(align=True)
        col.prop(scene, "frame_start", text="start:")
        col.prop(scene, "frame_end", text="end:")
        row = layout.row()
        row.prop(scene.ImperiumProperties,
                 "number_of_frames", text="number of frames")

        # --- PATH --- #

        row = layout.row()
        row.prop(scene.ImperiumProperties, "result_path", text="path")

        # --- FINAL OPERATOR --- #
        row = layout.row()
        row.scale_y = 1.5
        row.operator("imperium.renderer", icon="PLAY", text="Render")


### --- REGISTRATION AND UNREGISTRATION OF CLASSES --- ###


def register():
    bpy.utils.register_class(ImperiumRenderer)
    bpy.utils.register_class(ImperiumPanel)

    bpy.utils.register_class(ImperiumProperties)
    bpy.types.Scene.ImperiumProperties = bpy.props.PointerProperty(
        type=ImperiumProperties)


def unregister():
    bpy.utils.unregister_class(ImperiumRenderer)
    bpy.utils.unregister_class(ImperiumPanel)

    bpy.utils.unregister_class(ImperiumProperties)
    del bpy.types.Scene.ImperiumProperties


if __name__ == "__main__":
    register()
