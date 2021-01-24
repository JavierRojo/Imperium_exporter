function [combined_level_im, combined_player_im, combined_im, combined_alpha] = combine_img(colnames, in_color, in_lvl, in_player, n_frames, resolution_sprite) 
  
  % Combina los distintos sprites en una sola imagen para trabajar con ella.
  % colnames es una lista de nombres de archivos
  % in_color es la carpeta bajo la cual están las imágens de color.
  % in_lvl es la carpeta bajo la cual están las imágenes de nivel.
  % in_player es la carpeta bajo la cual están las imágenes de jugador.
  % n_frames indica cuántos fotograms de alto componen ImIx.
  % resolution_sprite es el ancho y alto de los sprites que componen ImIx.
  
  combined_im = zeros(resolution_sprite*n_frames,resolution_sprite*8,3,"uint8");
  combined_alpha = zeros(resolution_sprite*n_frames,resolution_sprite*8,"uint8");
  combined_level_im = zeros(resolution_sprite*n_frames,resolution_sprite*8,"uint8");
  combined_player_im = zeros(resolution_sprite*n_frames,resolution_sprite*8,"uint8");
  for i = 1:n_frames %Para todos los fotogramas
    for j = 1:8 % Para todas las direcciones cardinales
        file = name_from_cell(strcat(int2str(j),"_",int2str(i),"\.png"),colnames);
        [im, ~, alphaim] = imread(strcat(in_color,file));
        [~, ~, level_mask] = imread(strcat(in_lvl,file));
        [~, ~, player_mask] = imread(strcat(in_player,file));
        inf_row = ((i-1)*resolution_sprite)+1;
        sup_row = i*resolution_sprite;
        inf_col = ((j-1)*resolution_sprite)+1;
        sup_col = j*resolution_sprite;
        combined_im(inf_row:sup_row, inf_col:sup_col,:) = im(:,:,:);
        combined_alpha(inf_row:sup_row, inf_col:sup_col,:) = alphaim(:,:,:);
        combined_level_im(inf_row:sup_row, inf_col:sup_col,:) = level_mask(:,:,:);
        combined_player_im(inf_row:sup_row, inf_col:sup_col,:) = player_mask(:,:,:);
     endfor
  endfor  
endfunction