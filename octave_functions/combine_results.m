function [ImIx,ImMap] = combine_results(ImMap, ImMap_lvl, ImIx_ply, ImIx_lvl, ImIx, combined_level_im, combined_player_im, combined_alpha, n_level_colors)
  % combina los resultados de las matrices de color, nivel y jugador.
  
  ImMap = [ImMap;ImMap_lvl];  
  level_mask = logical(combined_level_im);
  player_mask = logical(combined_player_im);  
  ImIx(level_mask) = ImIx_lvl(level_mask)+(256 - 64 - n_level_colors -2);
  ImIx = ImIx+64+2;
  
  ImIx(player_mask) = ImIx_ply(player_mask);

  % Transform ImMap into a 128 table
  tmp_ImMap = ImMap;
  ImMap = zeros(256,3);
  ImMap((64+2)+1:end,:)=tmp_ImMap;
  ImMap(64+1,:) = [0, 1, 0];
  ImMap(64+2,:) = [1, 0, 1];
  
  display("setting alpha");
  alpha_mask = combined_alpha<0.1;
  ImIx(alpha_mask) = 64+1;

  % --- Put grayscale color for 64 player colors --- %
  ImMap(1:64,:) = generate_gray_matrix(64);
  
  
 endfunction