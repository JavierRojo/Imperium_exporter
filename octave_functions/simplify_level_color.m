function [ImIx_lvl,ImMap_lvl] = simplify_level_color(level_saturation, n_level_colors)
  % convierte a escala de grises y simplifica a n_level_colors kernels
  % level_saturation es una matriz de NxMx3
  
  graymap = rgb2gray(level_saturation);
  gray_im = uint8(zeros(size(graymap,1),size(graymap,2),3));
  gray_im(:,:,1) = graymap;
  gray_im(:,:,2) = graymap;
  gray_im(:,:,3) = graymap;

  [ImIx_lvl,ImMap_lvl] = rgb2ind(gray_im);
  ncenters_lvl = min(n_level_colors, size(ImMap_lvl,1));
  [nearcenter_lvl, centers_lvl, ~, ~] = kmeans (ImMap_lvl, ncenters_lvl);

  ImMap_lvl = centers_lvl;
  ImIx_lvl = nearcenter_lvl(ImIx_lvl+1);
 endfunction