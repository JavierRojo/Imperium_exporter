import bpy
import math
import os

bl_info = {
    "name": "Imperium Exporter",
    "description": "Un Add-on para renderizar texturas de Imperium",
    "author": "Javier Rojo Muñoz",
    "version": (2, 0),
    "location": "PROPERTIES > RENDER > IMPERIUM RENDERER",
    "warning": "Sólo funciona con Eeeve. En desarrollo.",
    "wiki_url": "https://github.com/JavierRojo/Imperium_exporter",
    "blender": (2, 81, 0),
    "category": "Render"
}

# -----------------------------------------------------------------------------------------------------
# --- FUNCTIONS --- #
def create_shadow_catcher():
    ''' Devuelve un material transparente que renderiza únicamente
    las sombras que recibe de otros objetos.
    '''
    # Si el material ya existe lo devolvemos directamente
    if bpy.data.materials.find("ImpMat_shadow_catcher") == 0:
        print("returning existing material")
        return bpy.data.materials["ImpMat_shadow_catcher"]

    # En cualquier otro caso lo generamos
    mat = bpy.data.materials.new(name="ImpMat_shadow_catcher")
    mat.use_nodes = True
    mat.shadow_method = 'NONE'
    mat.blend_method = 'BLEND'
        
    # Preparación del espacio de nodos
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
        
    # Output node
    node_output = nodes.new(type='ShaderNodeOutputMaterial') 
        
    # Mix node
    mix_shader = nodes.new(type="ShaderNodeMixShader")
    mix_shader.inputs[0].default_value = 0.75
    link = links.new(mix_shader.outputs[0], node_output.inputs[0])
        
        
    # Emission node
    shadow_color = nodes.new(type="ShaderNodeEmission")
    shadow_color.inputs[0].default_value = (1,1,1,1)
    link = links.new(shadow_color.outputs[0], mix_shader.inputs[1])
        
        
    # Diffuse node
    trans = nodes.new(type="ShaderNodeBsdfTransparent")
    link = links.new(trans.outputs[0], mix_shader.inputs[2])

    # Añadimos contraste al resultado
    # @TODO: utilizar una única fuente de luz y darle ángulo 0 o fijo
    ramp = nodes.new(type="ShaderNodeMath")
    ramp.operation = 'GREATER_THAN'
    ramp.inputs[1].default_value = 0.25
    link = links.new(ramp.outputs[0], mix_shader.inputs[0])
    
    # Conversor RGB -> BW
    rgb2bw = nodes.new(type="ShaderNodeRGBToBW")
    link = links.new(rgb2bw.outputs[0], ramp.inputs[0])
    
    # Conversor de Shader -> RGB
    shader2rgb = nodes.new(type="ShaderNodeShaderToRGB")
    link = links.new(shader2rgb.outputs[0], rgb2bw.inputs[0])
    
    # Diffuse node que calcula la sombra
    diffuse_origin = nodes.new(type="ShaderNodeBsdfDiffuse")
    diffuse_origin.inputs[0].default_value = (1,1,1,1)
    link = links.new(diffuse_origin.outputs[0], shader2rgb.inputs[0])
    return mat

def create_holdout(name_holdout_mat):
    ''' Define un material de tipo holdout con el nombre indicado'''

    # Si ya existe lo devolvemos directamente
    if bpy.data.materials.find(name_holdout_mat) == 0:
        return bpy.data.materials[name_holdout_mat]
    
    # En cualquier otro caso lo generamos
    mat = bpy.data.materials.new(name=name_holdout_mat)
    mat.use_nodes = True
    mat.shadow_method = 'OPAQUE'
    mat.blend_method = 'OPAQUE'
        
    # Inicializando el espacio de nodos
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
        
    # Output node
    node_output = nodes.new(type='ShaderNodeOutputMaterial') 
        
    # Mix node
    holdout = nodes.new(type="ShaderNodeHoldout")
    link = links.new(holdout.outputs[0], node_output.inputs[0])
    
    return mat

def create_emissive(name_emissive_mat):
    ''' Define un material de tipo emission con el nombre indicado'''

    # Si ya existe lo devolvemos directamente
    if bpy.data.materials.find(name_emissive_mat) == 0:
        return bpy.data.materials[name_emissive_mat]
    
    # En cualquier otro caso lo generamos
    mat = bpy.data.materials.new(name=name_emissive_mat) #set new material to variable
    mat.use_nodes = True
    mat.shadow_method = 'OPAQUE'
    mat.blend_method = 'BLEND'
        
    # Inicializando el espacio de nodos
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
        
    # Output node
    node_output = nodes.new(type='ShaderNodeOutputMaterial') 
        
    # Emission node
    emission = nodes.new(type="ShaderNodeEmission")
    emission.inputs[0].default_value = (1, 1, 1, 1)
    emission.inputs[1].default_value = 1

    link = links.new(emission.outputs[0], node_output.inputs[0])
    
    return mat

def default_values(cam):
    """ Valores por defecto de la cámara de Imperium Exporter. """
    cam.location = (-0.5, -4, 2.5)
    cam.rotation_euler = (math.pi*70/180, 0, 0)
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = 3
    cam.data.clip_end = 40
    return cam

# -----------------------------------------------------------------------------------------------------    
# --- IMPERIUM SET TO DEFAULT CAMERA --- #
class ImperiumSetToDefaultCamera(bpy.types.Operator):
    """ Modifica las características de la cámara seleccionada para que coincidan
    con los valores por defecto de Imperium renderer.
    """
    bl_idname = "imperium.convert_to_default_camera"
    bl_label = "Pone las propiedades de la cámara con los valores por defecto del Imperium Exporter."
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene

        if context.active_object and context.active_object.type != 'CAMERA':
            return {'CANCELLED'}

        cam = context.active_object
        # Los valores por defecto ofrecen una perspectiva pseudo isométrica
        scene.camera = default_values(cam)

        # La resolución de renderizado se ajusta a lo indicado por el usuario
        bpy.context.scene.render.resolution_x = scene.ImperiumProperties.width_frame
        bpy.context.scene.render.resolution_y = scene.ImperiumProperties.width_frame
        return {'FINISHED'}

# -----------------------------------------------------------------------------------------------------
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
            location=(0, 0, 0),
            rotation=(0, 0, 0)
        )
        # Referencia a la cámara recién creada y valores por defecto
        cam = bpy.data.objects[bpy.context.active_object.name]
        cam = default_values(cam)
        scene.camera = cam

        # La resolución de renderizado se ajusta a lo indicado por el usuario
        bpy.context.scene.render.resolution_x = scene.ImperiumProperties.width_frame
        bpy.context.scene.render.resolution_y = scene.ImperiumProperties.width_frame                
        return {'FINISHED'}

# -----------------------------------------------------------------------------------------------------
# --- IMPERIUM RENDERER --- #
class ImperiumRenderer(bpy.types.Operator):
    """ Renderiza los distintos Sprites a partir del modelo desde distintos
    ángulos y fotogramas de animación. El resultado se guarda en subcarpetas
    dentro del output folder.
    """

    bl_idname = "imperium.renderer"
    bl_label = "Imperium texture render"
    bl_options = {'REGISTER'}

    def execute(self, context):
        # Variables comúnmente utilizadas
        scene = context.scene
        n_frames = scene.ImperiumProperties.number_of_frames
        start = scene.frame_start
        end = scene.frame_end
        target = scene.ImperiumProperties.main_target

        # Comprobación de que hay un objetivo al que la cámara apunta
        bpy.ops.object.select_all(action='DESELECT')
        if(not target):
            self.report({'WARNING'}, "Debe declarar un target")
            return{'CANCELLED'}

        # Comprobación de que hay una cámara válida en escena
        if scene.ImperiumProperties.use_active_camera:
            cam = scene.camera
        else:
            cam = scene.ImperiumProperties.main_camera
        if (not cam):
            self.report({'WARNING'}, "Debe declarar una cámara")
            return{'CANCELLED'}

        # El renderizado siempre asume un fondo transparente
        scene.render.film_transparent = True

        # Divide la línea de tiempo en secciones lo más iguales posibles
        # @TODO: comprobar y/o arreglar el caso de n_frames=2
        stepvalue = round((end-start)/n_frames)
        frames = range(start, end, stepvalue)
        if(len(frames) < 1):
            frames = [start]
        
        # Almacena la rotación original para recuperarla tras cada operación
        original_rot = target.rotation_euler.copy()
        angle_step = math.pi*0.25

        def render_loop(folder_name):   
            """ Función auxiliar que describe el bucle de renderizado """
            # Generamos la subcarpeta si no existe
            if not os.path.exists(scene.ImperiumProperties.result_path+folder_name + "/"):
                os.mkdir(scene.ImperiumProperties.result_path + folder_name + "/")
                
            target.rotation_euler = original_rot.copy()
            count = 1
            for f in frames:
                # Set next frame of the animation sequence
                scene.frame_set(f)
                for deg in range(8):
                    # One iteration for each direction (clockwise)
                    target.rotation_euler[2] = -(deg)*angle_step

                    # Filepath based on frame and direction so matrix can be assembled
                    scene.render.filepath = scene.ImperiumProperties.result_path + folder_name +\
                        "/" + str(deg+1) + "_" + str(count)
                    try:
                        bpy.ops.render.render(write_still=True, use_viewport=False)
                    except:
                        self.report({'WARNING'}, "Could not render " + scene.render.filepath)
                        pass
                count += 1
            target.rotation_euler = original_rot.copy()

        def save_mats(prefix):
            """ Guarda los materiales de cada objeto y solo deja aquellos
            que empiecen con el prefijo indicado, sustituyéndolos por un material
            de emisión que se usará para generar las máscaras.
            """
            holdout = create_holdout("ImpMat_holdout")
            emission = create_emissive("ImpMat_emission")

            object_save_list = []
            for o in bpy.data.objects:
                if o.material_slots.values() == []:
                    continue
                else:                
                    save_list = []
                    for s in o.material_slots: 
                        save_list.append(s.material.name)
                        if s.material.name.startswith(prefix):
                            s.material = emission
                        else:
                            s.material = holdout
                    object_save_list.append([o,save_list])            
                o.material_slots.update()
            return object_save_list

        def load_mats(object_list):
            """ Recorremos toda la lista indicada devolviendo los
            materiales a su forma original.
            """            
            for e in object_list:
                slots = e[0].material_slots
                for s,orig_name in zip(slots,e[1]):   
                    s.material = bpy.data.materials[orig_name]           
                e[0].material_slots.update()  
            bpy.ops.object.select_all(action='DESELECT')


        # Base color loop
        if scene.ImperiumProperties.render_base:
            render_loop("color")
            
        # Level loop
        if scene.ImperiumProperties.render_level:            
            object_save_list = save_mats("ImpMat_level")
            render_loop("level")  
            load_mats(object_save_list)            
                      
        # Player loop
        if scene.ImperiumProperties.render_player:
            object_save_list = save_mats("ImpMat_player")  
            render_loop("player")  
            load_mats(object_save_list)                 
            
        # shadow loop
        # @TODO: Falta corregir el guardado en Octave   
        if scene.ImperiumProperties.render_shadow:     
            # Añadimos un plano para recibir la sombra       
            bpy.ops.mesh.primitive_plane_add(enter_editmode=False, location=(0, 0, 0))
            plane = bpy.data.objects[bpy.context.active_object.name]
            plane.scale = [10,10,10]
            shadow_catcher = create_shadow_catcher()
            plane.data.materials.append(shadow_catcher)
            plane.material_slots.update()
            
            holdout = create_holdout("ImpMat_holdout")
            object_save_list = []
            #@TODO: desactivar todas las luces menos el Sol. Activar Sol
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

            render_loop("shadow")

            # @TODO: reactivar todas las luces menos el Sol. ¿Desactivar el Sol?   
            load_mats(object_save_list)
            plane.select_set(True)
            bpy.ops.object.delete() 
        return {'FINISHED'}

# -----------------------------------------------------------------------------------------------------
# --- VARIABLES --- #
class ImperiumProperties(bpy.types.PropertyGroup):
    """ Propiedades para el add-on de Imperium Exporter """
    # Funciones de filtro para determinar el tipo de objeto
    def is_valid_target(self, object):
        if (self.mesh_as_target):
            return object.type == 'MESH'
        else:
            return object.type == 'EMPTY'

    def is_camera(self, object):
        return object.type == 'CAMERA'    
    
    def is_sun_light(self, object):
        return object.type == 'LIGHT' and object.data.type == 'SUN'

    # Por el momento el ancho es igual al alto
    # @TODO: permitir ancho y alto independientes. Comprobar Octave
    def define_width(self, context):
        bpy.context.scene.render.resolution_x = self.width_frame
        bpy.context.scene.render.resolution_y = self.width_frame
        return None

    # Número de fotogramas que queremos renderizar
    number_of_frames: bpy.props.IntProperty(
        name="Número de fotogramas para la animación",
        default=1,
        min=1,
        max=50
    )
    # Ancho, en píxeles, de cada Sprite.
    width_frame: bpy.props.IntProperty(
        name="Ancho, en píxeles, de cada Sprite",
        default=64,
        min=1,
        max=256,
        update=define_width,
        subtype='PIXEL'
    )
    # Carpeta de salida
    result_path: bpy.props.StringProperty(
        name="Carpeta de salida",
        default=".",
        description="En esta carpeta se generarán las distintas subcarpetas que contendrán los Sprites",
        subtype='DIR_PATH'
    )
    # Target para el render
    main_target: bpy.props.PointerProperty(
        name="Main target",
        description="Target que será utilizado como objetivo de la cámara",
        type=bpy.types.Object,
        poll=is_valid_target
    )
    # Booleno que decide si usar la malla como objetivo en lugar de un Empty
    mesh_as_target: bpy.props.BoolProperty(
        name="Use mesh as target",
        description="Booleno que decide si usar la malla como objetivo en lugar de un Empty",
        default=False
    )
    # Cámara encargada del renderizado
    main_camera: bpy.props.PointerProperty(
        name="Main camera",
        description="Cámara encargada del renderizado",
        type=bpy.types.Object,
        poll=is_camera
    )
    # Decide si usar la cámara activa de la escena o seleccionar una
    use_active_camera: bpy.props.BoolProperty(
        name="Use active camera",
        description="Decide si usar la cámara activa de la escena o seleccionar una",
        default=True
    )
    # Camera that will perform the render
    main_light: bpy.props.PointerProperty(
        name="Main light",
        description="Light that will cast the shadows",
        type=bpy.types.Object,
        poll=is_sun_light
    )
    # Decide si renderizar el color de base
    render_base: bpy.props.BoolProperty(
        name="Render base color",
        description="Decide si renderizar el color de base",
        default=False
    ) 
    # Decide si renderizar la máscara para la sombra
    render_shadow: bpy.props.BoolProperty(
        name="Render shadow texture",
        description="Decide si renderizar la máscara para la sombra",
        default=False
    )
    # Decide si renderizar la máscara para el color de nivel
    render_level: bpy.props.BoolProperty(
        name="Render level mask",
        description="Decide si renderizar la máscara para el color de nivel",
        default=False
    )    
    # Decide si renderizar la máscara para el color del jugador
    render_player: bpy.props.BoolProperty(
        name="Render player mask",
        description="Decide si renderizar la máscara para el color del jugador",
        default=False
    )

# -----------------------------------------------------------------------------------------------------
# --- UI IMPERIUM PANEL --- #
class ImperiumPanel(bpy.types.Panel):
    """ Panel principal para el Add-on. Está en la pestaña 'render' dentro de PROPERTIES """
    bl_idname = "OBJECT_PT_hello_world"
    bl_label = "Imperium renderer"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        # Variables comúnmente utilizadas
        layout = self.layout
        scene = context.scene

        # Versión del add-on
        layout.label(text="Version: 2.0", icon='SCRIPT')

        # --- FRAME PROPERTIES --- #
        box = layout.box()
        box.label(text="Información del fotograma")
        col = box.column(align=True)
        col.prop(scene, "frame_start", text="inicio")
        col.prop(scene, "frame_end", text="fin")
        col.prop(scene.ImperiumProperties,
                 "number_of_frames", text="número de fotogramas")
        row = box.row()
        row.prop(scene.ImperiumProperties, "width_frame", text="ancho")

        # --- TARGET --- #
        layout.row()
        box = layout.box()
        box.label(text="Target")
        row = box.row()
        box.prop(scene.ImperiumProperties,
                 "mesh_as_target", text="look for meshes")

        # Un icono difrente se aplica para cada tipo de target
        if scene.ImperiumProperties.mesh_as_target:
            box.prop(scene.ImperiumProperties, "main_target",
                     text="", icon='MESH_CUBE')
        else:
            box.prop(scene.ImperiumProperties,
                     "main_target", text="", icon='TRACKER')

        # --- CAMERA --- #
        row = layout.row()
        box = layout.box()
        box.label(text="Cámara")

        # Si no estamos en el modo objetio, no se puede agregar ninguna cámara
        if context.mode == 'OBJECT':
            # Si se selecciona una cámara se propone su modifiación en lugar de crear una nueva
            if context.active_object and context.active_object.type == 'CAMERA':
                box.operator("imperium.convert_to_default_camera",
                             icon="OUTLINER_DATA_CAMERA", text="Convertir a cámara por defecto")
            else:
                box.operator("imperium.default_camera",
                             icon="OUTLINER_DATA_CAMERA", text="Generar cámara por defecto")
        row = box.row()
        row.prop(scene.ImperiumProperties, "use_active_camera", text="use active camera")

        # Si no se usa la cámara activa, se permite seleccionar una
        if not scene.ImperiumProperties.use_active_camera:
            row.prop(scene.ImperiumProperties, "main_camera",
                     text="camera", icon='OUTLINER_DATA_CAMERA')

        # --- PATH --- #
        box = layout.box()
        box.label(text="Parámetros de salida")
        box.prop(scene.ImperiumProperties, "result_path", text="")
        box.prop(scene.ImperiumProperties, "render_base", text="Renderizar color base")
        box.prop(scene.ImperiumProperties, "render_shadow", text="Renderizar máscara de sombra")
        if scene.ImperiumProperties.render_shadow:
            box.prop(scene.ImperiumProperties, "main_light",icon='LIGHT_SUN')
            
        box.prop(scene.ImperiumProperties, "render_level", text="Renderizar máscara de nivel")
        box.prop(scene.ImperiumProperties, "render_player", text="Renderizar máscara de jugador")

        # --- FINAL OPERATOR --- #
        row = layout.row()
        row.scale_y = 1.5
        row.operator("imperium.renderer", icon="PLAY", text="Renderizar")

# -----------------------------------------------------------------------------------------------------
### --- REGISTRO Y CIERRE DE CLASES --- ###
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
