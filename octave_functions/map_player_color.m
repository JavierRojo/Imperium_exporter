function hsv_res = map_player_color(hsv_player)
  % hsv_player es una matriz de colores en decimal (NxMx3) con información hsv.
  hsv_res = hsv_player;
  min_player_float = 0.75;    
  hsv_res(:,:,2) = min_player_float + (hsv_player(:,:,2) .* (1 - min_player_float) );
 endfunction