function m_res = map_lvl_color(min_lvl, m)
  % min_lvl (0-255) es el mínimo que considera imperium en un gris para marcarlo como color de nivel.
  % m es una matriz de colores en decimal (Nx3) en la que idealmente todos los colores son grises. 

  % @TODO: check MIN_LVL_COLOR + x * ((255-72)/255)
  min_lvl_float = (min_lvl/255.0);  
  m_res = min_lvl_float + (m .* (1 - min_lvl_float));  
endfunction