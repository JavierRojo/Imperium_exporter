import bpy

bl_info = {
    "name": "Imperium exporter",
    "description": "An add-on for rendering Imperium textures",
    "author": "Javier Rojo Muñoz",
    "version": (0, 1),
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
        scene.render.filepath = scene.ImperiumProperties.result_path + \
            "frame"+str(scene.ImperiumProperties.frame_to_render)
        scene.frame_set(scene.ImperiumProperties.frame_to_render)
        bpy.ops.render.render(write_still=True, use_viewport=False)
        return {'FINISHED'}


### --- VARIABLES CLASS --- ###


class ImperiumProperties(bpy.types.PropertyGroup):
    """Properties for this addon"""
    frame_to_render: bpy.props.IntProperty(
        name="Frame to render",
        default=1
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
        ### --- FIRST ITERATION --- ###
        layout.label(text="T1-01", icon='SCRIPT')

        # --- FRAME PROPERTIES --- #
        row = layout.row()
        # layout.label(text="Camera properties:")
        # col = layout.column(align=True)
        # col.prop(scene, "frame_start", text="start:")
        # col.prop(scene, "frame_end", text="end:")
        # row = layout.row()
        # @TODO:evenly spaced frames given number of frames
        #       layout.label(text="Number of frames: @TODO")

        # @TODO: delete this line and substitute it with the above
        # layout.label(text="Frame to render:")

        row.prop(scene.ImperiumProperties, "frame_to_render", text="frame")

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
