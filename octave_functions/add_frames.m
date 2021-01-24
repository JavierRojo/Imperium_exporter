function ImIx_f = add_frames(ImIx, n_frames,resolution_sprite)
  
  
  % Añade frames de 1px de ancho entre los sprites de la imagen.
  % ImIx es la imagen a la que vamos a añadir los marcos con índices a una tabla de colores.
  % n_frames indica cuántos fotograms de alto componen ImIx.
  % resolution_sprite es el ancho y alto de los sprites que componen ImIx.
  FRAMES_IX = 64+2;
  ImIx_f = zeros(size(ImIx,1)+n_frames-1, size(ImIx,2)+7)+1;
  for i=1:n_frames
    for j=1:8
      if i==1
        if j == 1
          ImIx_f((i-1)*resolution_sprite+i:(i)*resolution_sprite, (j-1)*resolution_sprite+j:(j)*resolution_sprite) = ...
          ImIx((i-1)*resolution_sprite+1:(i)*resolution_sprite, (j-1)*resolution_sprite+1:(j)*resolution_sprite);
        else
          ImIx_f((i-1)*resolution_sprite+i:(i)*resolution_sprite+i-1, (j-1)*resolution_sprite+j:(j)*resolution_sprite+j-1) = ...
          ImIx((i-1)*resolution_sprite+1:(i)*resolution_sprite, (j-1)*resolution_sprite+1:(j)*resolution_sprite);
        endif
      else
        if j == 1
          ImIx_f((i-1)*resolution_sprite+i:(i)*resolution_sprite+i-1, (j-1)*resolution_sprite+j:(j)*resolution_sprite) = ...
          ImIx((i-1)*resolution_sprite+1:(i)*resolution_sprite, (j-1)*resolution_sprite+1:(j)*resolution_sprite);
        else
          ImIx_f((i-1)*resolution_sprite+i:(i)*resolution_sprite+i-1, (j-1)*resolution_sprite+j:(j)*resolution_sprite+j-1) = ...
          ImIx((i-1)*resolution_sprite+1:(i)*resolution_sprite, (j-1)*resolution_sprite+1:(j)*resolution_sprite);
        endif
      endif
    endfor
  endfor


  frames_i = resolution_sprite+1:resolution_sprite+1:n_frames*resolution_sprite+n_frames-1;
  frames_j = resolution_sprite+1:resolution_sprite+1:7*resolution_sprite+7;
  ImIx_f(:,frames_j) = FRAMES_IX;
  ImIx_f(frames_i,:) = FRAMES_IX; 
  
endfunction