pkg load statistics;
close all;
clear all;
clc;

% --- CONFIGURATION --- %
% Load configuration from .cfg file
originalFolder = pwd();
display("loading configuration file");
configurationFile = "./configuration.cfg";
run(configurationFile);
input_folder_color = strcat(input_folder,"color/");
input_folder_level = strcat(input_folder,"level/");
input_folder_player = strcat(input_folder,"player/");

if size(input_folder_color,1) == 0
  [colnames, input_folder_color, ~] = uigetfile ("MultiSelect", "ON");
  cd(input_folder_color)
  colnames = reshape(colnames,size(colnames,2),size(colnames,1));
else
  cd(input_folder_color);
  colnames_color = glob("*[0-9]_[0-9]*.png");
  cd(originalFolder)
  cd(input_folder_level);
  colnames_level = glob("*[0-9]_[0-9]*.png");
  cd(originalFolder)
  cd(input_folder_player);
  colnames_player = glob("*[0-9]_[0-9]*.png");
endif
cd(originalFolder)
addpath(strcat(pwd,"/octave_functions"));

% --- COMBINE PNG TEXTURES --- %
display("combining png images");
combined_im = zeros(resolution_sprite*n_frames,resolution_sprite*8,3,"uint8");
combined_alpha = zeros(resolution_sprite*n_frames,resolution_sprite*8,"uint8");
combined_level_im = zeros(resolution_sprite*n_frames,resolution_sprite*8,"uint8");
combined_player_im = zeros(resolution_sprite*n_frames,resolution_sprite*8,"uint8");
for i = 1:n_frames %for every frame
  for j = 1:8 %for every direction
      file = name_from_cell(strcat(int2str(j),"_",int2str(i),"\.png"),colnames_color);
      [im, ~, alphaim] = imread(strcat(input_folder_color,file));
      [~, ~, level_mask] = imread(strcat(input_folder_level,file));
      [~, ~, player_mask] = imread(strcat(input_folder_player,file));
      inf_row = ((i-1)*resolution_sprite)+1;
      sup_row = i*resolution_sprite;
      inf_col = ((j-1)*resolution_sprite)+1;
      sup_col = j*resolution_sprite;
      combined_im(inf_row:sup_row, inf_col:sup_col,:) = im(:,:,:);
      combined_alpha(inf_row:sup_row, inf_col:sup_col,:) = alphaim(:,:,:);
      combined_level_im(inf_row:sup_row, inf_col:sup_col,:) = level_mask(:,:,:);
      combined_player_im(inf_row:sup_row, inf_col:sup_col,:) = player_mask(:,:,:);
      %combined image in format 0-255
   endfor
endfor



% --- ALPHA CONTRAST AND COMBINATION WITH RGB --- %
display("adjusting alpha");
combined_alpha = floor((combined_alpha./255)+0);
combined_level_im = floor((combined_level_im./255)+0);
combined_player_im = floor((combined_player_im./255)+0);
triple_level_combined = cat(3,combined_level_im,combined_level_im,combined_level_im);
triple_player_combined = cat(3,combined_player_im,combined_player_im,combined_player_im);
triple_alpha = cat(3,combined_alpha,combined_alpha,combined_alpha);
combined_im = combined_im .* triple_alpha;
combined_im(:,:,2) = combined_im(:,:,2) + ((1-combined_alpha).*255);


% --- COLOR SIMPLIFICATION --- %
display("simplifying colors");
%Delete colors that won't be used (LEVEL)
level_saturation = combined_im .* triple_level_combined;
combined_im = combined_im .* (1-triple_level_combined);
combined_im(:,:,2) = combined_im(:,:,2) + combined_level_im.*255;

%Delete colors that won't be used (PLAYER)
player_saturation = combined_im .* triple_player_combined;
combined_im = combined_im .* (1-triple_player_combined);
combined_im(:,:,2) = combined_im(:,:,2) + combined_player_im.*255;


%Simplify all the other colors
[ImIx,ImMap] = rgb2ind(combined_im);
ncenters = min((256-64)-2-n_level_colors, size(ImMap,1));
[nearcenter, centers, ~, ~] = kmeans (ImMap, ncenters);


% ImIx marca los índices a la lista grande original de colores de la imagen.
% ImMap is in double
% combined_im is in uint8
ImMap = centers;
ImIx = nearcenter(ImIx+1);

% --- COLOR SIMPLIFICATION LEVEL COLOR--- %
display("simplifying colors of level color texture");
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
% @TODO: do it right
% --- COLOR SIMPLIFICATION PLAYER COLOR--- %
display("simplifying colors of player color texture");
hsv_player = rgb2hsv (player_saturation);
% Colors in table (0-63) don't matter, only the index in the image
sat = hsv_player(:,:,2);
val = hsv_player(:,:,3);
% 0.9999 prevents the saturation=1 case
ImIx_ply = floor(val *0.99999 * 8)*8 + floor(sat*0.99999*8);


% --- COMBINATION OF LEVEL AND COLOR AND PLAYER --- %
ImMap = [ImMap;ImMap_lvl];
%ImIx
%ImIx_lvl
%ImIx_ply
level_mask = logical(combined_level_im);
player_mask = logical(combined_player_im);
ImIx(level_mask) = ImIx_lvl(level_mask)+180;
ImIx = ImIx+64+2;
ImIx(player_mask) = ImIx_ply(player_mask); % from 0-63 to 1-64
%%@TODO: do not use magic numbers

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
c = ones(64,3);
for i = 1:64
  c(i,:) = c(i,:)*i/64;
endfor
ImMap(1:64,:) = c;


% --- FRAMES --- %
% 
% ooo|ooo|ooo
% ooo|ooo|ooo
% ooo|ooo|ooo
% ---*---*---
% ooo|ooo|ooo
% ooo|ooo|ooo
% ooo|ooo|ooo
% ---*---*---
% ooo|ooo|ooo
% ooo|ooo|ooo
% ooo|ooo|ooo
% 
disp("adding frames");
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
ImIx_f(:,frames_j)=64+2;
ImIx_f(frames_i,:)=64+2;
% --- SAVE IMAGE --- %
cd(originalFolder)
cd(output_folder)
imwrite(ImIx_f,ImMap,"resultado_final.BMP");%,"Alpha",combined_alpha)
cd(originalFolder)
rmpath(strcat(pwd,"/octave_functions"));